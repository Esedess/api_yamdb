from rest_framework import serializers

from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

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


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False)
    confirmation_code = serializers.CharField(allow_blank=False)
