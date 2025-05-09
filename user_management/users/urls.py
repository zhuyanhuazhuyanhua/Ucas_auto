from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, InterestViewSet, activate  # 导入 activate 函数

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'interests', InterestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('activate/<str:token>', activate, name='activate'),  # 直接使用 activate 函数
] 