from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное поле. 150 символов или меньше.'
            'Только буквы, цифры и @/./+/-/_'),
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
    )
    confirmation_code = models.CharField(
        max_length=20,
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role[0]) for role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        help_text=(
            'Роль пользователя на ресурсе.'
            'User, Moderator или Admin'
            'Изменить роль может только Admin'
        )
    )
    bio = models.TextField(
        'О себе',
        blank=True,
        help_text='Расскажите немного о себе.'
    )

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    @property
    def is_admin(self):
        """Superuser is always an admin and a moderator."""
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        """The admin is always a moderator."""
        return self.role == self.MODERATOR or self.role == self.ADMIN

    def __str__(self):
        return self.username
