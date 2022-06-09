from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser


def get_tokens_for_user(user):
    """
    Generates a token.
    Args - user.
    Return dict('token': str(token)).
    """
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token),
    }


def send_confirmation_code(user):
    """
    Sends mail.
    Args - User object.
    """
    username = user.username
    user_email = (user.email, )
    confirmation_code = user.confirmation_code
    from_email = settings.DEFAULT_FROM_EMAIL

    subject = f'{username}! YaMDb прислал вам код подтверждения!'
    message = f'Код подтверждения - {confirmation_code}'

    send_mail(
        subject,
        message,
        from_email,
        user_email,
        fail_silently=False,
    )


def user_check(data):
    """
    User check.
    Checks that the user with the specified username and mail
    is in the database.
    Args - serializer.validated_data.
    Return User object or ValidationError.
    """
    try:
        user, _ = CustomUser.objects.get_or_create(
            **data)
    except IntegrityError as error:
        message = error
        if 'email' in error.args[0]:
            message = 'Не верный email'
        if 'username' in error.args[0]:
            message = 'Не верное имя пользователя'
        raise ValidationError(message)

    return user
