import re
from datetime import datetime

from django.core.exceptions import ValidationError


def username_validator(value):
    """
    "me" is not allowed as a username.
    150 characters or fewer. Letters, digits and @/./+/-/_ only.
    """
    if value == 'me':
        message = (
            'Введенное имя пользователя не корректно. '
            "Имя 'me' не разрешено.")
        raise ValidationError(message)
    if not re.match(r'^[\w.@+-]+$', value):
        message = (
            'Введенное имя пользователя не корректно. '
            'Используйте только буквы, цифры и @/./+/-/_. '
            '150 символов или меньше.')
        raise ValidationError(message)


def year_validator(value):
    current_year = datetime.today().year
    if value > current_year:
        message = (
            'Нельзя добавлять произведения, которые еще не вышли.'
            f'Год выпуска {value} не может быть больше текущего.')
        raise ValidationError(message)
