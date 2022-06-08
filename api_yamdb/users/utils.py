from django.core.mail import send_mail
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


def send_confirmation_code(email, confirmation_code):
    """
    Sends mail.
    Args - str(email), str(confirmation_code).
    """
    send_mail(
        'Ваш код подтверждения',
        f'Код подтверждения - {confirmation_code}',
        'noreply@yamdb',
        [email],
        fail_silently=False,
    )


def user_check(request):
    """
    User check.
    Checks that the user with the specified username and mail
    is in the database.
    Args - request.
    Return User object os False.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    try:
        user = CustomUser.objects.get(username=username, email=email)
    except CustomUser.DoesNotExist:
        return False
    return user
