from django.contrib.auth import get_user_model
from django.db.models import Avg, Q
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
from .permissions import (
    IsAdmin, IsAdminModeratorOwnerOrReadOnly, IsAdminOrReadOnly,
)
from .serializers import (
    CategorуSerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    SignUpSerializer, TitleCreateUpdateSerializer, TitleSerializer,
    TokenSerializer, UserSerializer,
)
from reviews.models import Categorу, Genre, Review, Title

User = get_user_model()


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
    username, email = serializer.validated_data.values()
    if User.objects.filter(
        (Q(email=email) | Q(username=username)),
        ~Q(**serializer.validated_data)
    ).exists():
        return Response(
            {'Enter the correct pair of username and email.'},
            status=status.HTTP_400_BAD_REQUEST)
    user, _ = User.objects.get_or_create(**serializer.validated_data)
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
    if serializer.is_valid():
        username, confirmation_code = serializer.validated_data.values()
        user = get_object_or_404(User, username=username)
        if confirmation_code != str(user.confirmation_code):
            message = 'Не верный код'
            raise serializers.ValidationError(message)
        refresh = RefreshToken.for_user(user)
        token = {'token': str(refresh.access_token)}
        return Response(token, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        if request.method == 'PATCH':
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
    permission_classes = (IsAdminOrReadOnly,)
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
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.all().annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly, )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review,
            id=review_id,
            title_id=title_id
        )
        serializer.save(author=self.request.user, review=review)
