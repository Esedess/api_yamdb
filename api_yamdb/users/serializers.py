from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from .utils import user_check
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(UnicodeUsernameValidator,),
        allow_null=False,
        allow_blank=False,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        allow_null=False,
        allow_blank=False,
    )

    def validate_username(self, value):
        """
        "me" is not allowed as a username.
        """
        if value.lower() == 'me':
            message = 'Выберите другое имя пользователя'
            raise serializers.ValidationError(message)

        return value

    def validate_role(self, value):
        """
        Only the admin can change roles.
        """
        request = self.context['request']

        if request.user.is_staff or request.user.role == 'admin':
            return value

        return 'user'

    def create(self, validated_data):
        """
        Creates a user.
        """
        user = user_check(validated_data)

        return user

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False)
    confirmation_code = serializers.CharField(allow_blank=False)
