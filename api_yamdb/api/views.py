from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminModeratorOwnerOrReadOnly, ReadOnly
from .serializers import (
    CategorуSerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    SignUpSerializer, TitleCreateUpdateSerializer, TitleSerializer,
    TokenSerializer, UserSerializer,
)
from reviews.models import Categorу, Genre, Review, Title, User


@api_view(['POST', ])
@permission_classes([permissions.AllowAny])
def signup_user(request):
    """
    Creates a user and sends a confirmation code to the email.
    If the user is already in the database
    sends a confirmation code to the user's email again.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        return Response(
            {'Введена не правильная пара имени пользователя и e-mail.'},
            status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = get_random_string(length=20)
    user.confirmation_code = confirmation_code
    user.save()
    subject = 'Ваш код подтверждения регистрации на YaMDb!'
    message = f'Код подтверждения - {user.confirmation_code}'
    user.email_user(subject, message, fail_silently=False)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([permissions.AllowAny])
def user_token(request):
    """
    Creates a token at the user's request.
    Checks the user in the database by username, checks the confirmation code.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username, confirmation_code = serializer.validated_data.values()
    user = get_object_or_404(User, username=username)
    if confirmation_code != user.confirmation_code:
        message = 'Не верный код'
        raise serializers.ValidationError(message)
    refresh = RefreshToken.for_user(user)
    token = {'token': str(refresh.access_token)}
    return Response(token, status=status.HTTP_201_CREATED)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, )
    pagination_class = pagination.PageNumberPagination

    @action(methods=['get', 'PATCH'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='me', url_name='me')
    def personal_profile(self, request, *args, **kwargs):
        """
        Requester's account information.
        With a GET request,
        it returns the credentials of the requester's account.
        On a PATCH request,
        updates the requester's account information.
        """
        instance = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=instance.role)
        return Response(serializer.data)


class CategoryAndGenreViewSetsDaddy(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    permission_classes = (ReadOnly | IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategorуViewSet(
    CategoryAndGenreViewSetsDaddy
):
    queryset = Categorу.objects.all()
    serializer_class = CategorуSerializer


class GenreViewSet(
    CategoryAndGenreViewSetsDaddy
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (ReadOnly | IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('rating',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=self.kwargs.get('review_id'),
                title_id=self.kwargs.get('title_id')
            )
        )
