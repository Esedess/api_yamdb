from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import username_validator

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное поле. 150 символов или меньше.'
            'Только буквы, цифры и @/./+/-/_'),
        validators=(username_validator,),
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField(
        'О себе',
        blank=True,
        help_text='Расскажите немного о себе.'
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
    confirmation_code = models.CharField(
        max_length=20,
    )

    class Meta:
        ordering = ('-username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class CategoryAndGenreDaddy(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Categorу(CategoryAndGenreDaddy):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryAndGenreDaddy):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Наименование',
    )
    year = models.IntegerField(
        verbose_name='Год',
        validators=(
            MaxValueValidator(
                int(datetime.now().year),
                'Произведения из будущего не принимаем'
            ),
        )
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        through='GenreTitle',
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        Categorу,
        verbose_name='Категория произведения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        verbose_name='Наименование жанра',
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Наименование произведения',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

    def __str__(self):
        return f'{self.genre}, произведение - {self.title}'


class ReviewAndCommentDaddy(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.text[:20]


class Review(ReviewAndCommentDaddy):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор отзыва',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        default=0,
        validators=(
            MaxValueValidator(10, 'Значения рейтинга от 1 до 10'),
            MinValueValidator(1, 'Значения рейтинга от 1 до 10')
        )
    )
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title_id'),
                name='unique_title_id'
            )
        ]


class Comment(ReviewAndCommentDaddy):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
