from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategorуViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    UsersViewSet, signup_user, user_token,
)

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategorуViewSet, basename='categories')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', signup_user, name='signup_user'),
    path('v1/auth/token/', user_token, name='token'),
]
