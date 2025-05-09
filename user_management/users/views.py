from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Interest, UserInterest
from .serializers import (
    UserSerializer, UserUpdateSerializer, PasswordChangeSerializer,
    InterestSerializer, InterestUpdateSerializer
)
import jwt
from datetime import datetime, timedelta
import smtplib
from email.utils import parseaddr

User = get_user_model()

@api_view(['GET'])
def activate(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        if not user.is_active:
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully'})
        return Response({'message': 'Account is already activated'})
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'login', 'showinterest']:  # 确保 showinterest 方法权限正确
            return [permissions.AllowAny()] if self.action in ['create', 'login'] else [permissions.IsAuthenticated()]
        return super().get_permissions()

    def validate_email_format(self, email):
        """验证邮箱格式是否正确"""
        parsed = parseaddr(email)
        return '@' in parsed[1]

    def validate_email_exists(self, email):
        """通过 SMTP 验证邮箱是否存在"""
        try:
            # 获取邮件服务器域名
            domain = email.split('@')[1]
            # 连接到 SMTP 服务器
            server = smtplib.SMTP()
            server.connect(f'smtp.{domain}')
            server.helo()
            server.mail('')
            code, message = server.rcpt(email)
            server.quit()
            return code == 250
        except Exception as e:
            return False

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            # 验证邮箱格式
            if not self.validate_email_format(email):
                return Response({'error': '邮箱格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
            # 验证邮箱是否已存在于数据库
            if User.objects.filter(email=email).exists():
                return Response({'error': '该邮箱已被注册'}, status=status.HTTP_400_BAD_REQUEST)
            # 通过 SMTP 验证邮箱是否存在
            if not self.validate_email_exists(email):
                return Response({'error': '邮箱不存在，请检查输入'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            # Generate activation token
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=1)
            }, settings.SECRET_KEY, algorithm='HS256')
            
            # Send activation email
            activation_url = f"{settings.FRONTEND_URL}/{token}"
            send_mail(
                'Activate your account',
                f'Click here to activate your account: {activation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({'error': 'Account is not activated'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.check_password(password):
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def showinterest(self, request):
        user_interests = UserInterest.objects.filter(user=request.user).order_by('order')
        if user_interests.count() <= 10:
            interests = user_interests
        else:
            interests = user_interests.order_by('?')[:10]
        serializer = InterestSerializer([interest.interest for interest in interests], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_interests(self, request):
        serializer = InterestUpdateSerializer(data=request.data)
        if serializer.is_valid():
            interest_ids = serializer.validated_data.get('interest_ids', [])
            interest_names = serializer.validated_data.get('interest_names', [])
            failed_interests = []

            # 根据兴趣名称查找对应的兴趣 ID，若不存在则创建
            for name in interest_names:
                try:
                    interest = Interest.objects.get(name=name)
                    interest_ids.append(interest.id)
                except Interest.DoesNotExist:
                    try:
                        interest = Interest.objects.create(name=name)
                        interest_ids.append(interest.id)
                    except Exception as e:
                        failed_interests.append(name)
                        continue

            # 去重
            interest_ids = list(set(interest_ids))

            # 删除现有兴趣
            UserInterest.objects.filter(user=request.user).delete()

            # 添加新兴趣并排序
            for order, interest_id in enumerate(interest_ids):
                try:
                    interest = Interest.objects.get(id=interest_id)
                    UserInterest.objects.create(
                        user=request.user,
                        interest=interest,
                        order=order
                    )
                except Interest.DoesNotExist:
                    failed_interests.append(str(interest_id))

            if failed_interests:
                return Response({'message': '部分兴趣更新失败', 'failed_interests': failed_interests}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': '兴趣更新成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticated]
