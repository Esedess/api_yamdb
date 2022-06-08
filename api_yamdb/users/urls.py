from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, signup_user, user_token

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/signup/', signup_user, name='signup_user'),
    path('auth/token/', user_token, name='token'),
]
