from rest_framework import (
    exceptions, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import CustomUser
from .permissions import IsAdminOnly
from .serializers import TokenSerializer, UserSerializer
from .utils import get_tokens_for_user, send_confirmation_code, user_check


@api_view(['POST', ])
@permission_classes([permissions.AllowAny])
def signup_user(request):
    """
    Creates a user and sends a confirmation code to the email.
    If the user is already in the database
    sends a confirmation code to the user's email again.
    """
    user = user_check(request)
    if user:
        confirmation_code = user.confirmation_code
        email = user.email
        send_confirmation_code(email, confirmation_code)

        return Response('Check your email', status=status.HTTP_200_OK)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        email = serializer.validated_data.get('email')
        confirmation_code = serializer.data.get('confirmation_code')
        send_confirmation_code(email, confirmation_code)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes([permissions.AllowAny])
def user_token(request):
    """
    Creates a token at the user's request.
    Checks the user in the database by username, checks the confirmation code.
    """
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            message = 'Пользователя с таким username не существует'
            raise exceptions.NotFound(message)
        if confirmation_code != str(user.confirmation_code):
            message = 'Не верный код'
            raise serializers.ValidationError(message)
        token = get_tokens_for_user(user)

        return Response(token, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly, )
    pagination_class = pagination.PageNumberPagination

    def perform_create(self, serializer):
        """
        Checks the role when creating a user.
        If new user is Admin puts is_staff = True.
        """
        role = serializer.validated_data.get('role')
        if role == 'admin':
            serializer.save(is_staff=True)
        else:
            serializer.save(is_staff=False)

    def perform_update(self, serializer):
        """
        Checks the role when updating user data.
        If the user has become an Admin, it puts is_staff = True.
        If the user has stopped being an Admin, put is_staff = False.
        """
        role = serializer.validated_data.get('role')
        if role == 'admin':
            serializer.save(is_staff=True)
        else:
            serializer.save(is_staff=False)

    @action(methods=['get', 'PATCH'],
            detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='me', url_name='me_patch')
    def me_retrieve(self, request, *args, **kwargs):
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
            self.perform_update(serializer)

        return Response(serializer.data)
