from rest_framework import serializers
from .models import User, Interest, UserInterest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'  # 或指定具体字段

class UserInterestSerializer(serializers.ModelSerializer):
    interest = InterestSerializer()

    class Meta:
        model = UserInterest
        fields = ['interest', 'order']

class UserSerializer(serializers.ModelSerializer):
    interests = UserInterestSerializer(source='userinterest_set', many=True, read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'avatar', 'interests']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'avatar']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class InterestUpdateSerializer(serializers.Serializer):
    interest_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    interest_names = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate(self, data):
        if not data.get('interest_ids') and not data.get('interest_names'):
            raise serializers.ValidationError("Either 'interest_ids' or 'interest_names' must be provided.")
        return data