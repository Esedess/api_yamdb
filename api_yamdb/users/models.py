import uuid

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **other_fields):
        if not email:
            raise ValueError('Users must have an email address')

        if username == 'me':
            raise ValueError('"me" is not allowed as a username')

        email = self.normalize_email(email)
        role = other_fields.get('role')

        if role == 'admin':
            other_fields.setdefault('is_staff', True)

        user = self.model(
            username=username,
            email=email,
            **other_fields,
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **other_fields):
        other_fields.setdefault('role', 'admin')
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser is_staff mast be True'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser is_superuser mast be True'
            )

        return self.create_user(username, email, password, **other_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        help_text=(
            'Обязательное поле! 150 символов или меньше.'
            'Только буквы, цифры и @/./+/-/_.'
            'Использовать имя "me" в качестве username запрещено.'
        )
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='eMail',
        help_text='Обязательное поле! Введите действительный email.'
    )
    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль',
        help_text=(
            'Роль пользователя на ресурсе.'
            'User, Moderator или Admin'
            'Изменить роль может только Admin'
        )
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
        help_text='Ваше имя.'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
        help_text='Ваша фамилия.'
    )
    bio = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='О себе',
        help_text='Расскажите немного о себе.'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
