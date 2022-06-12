from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import ASCIIUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Categorу, Comment, Genre, Review, Title

User = get_user_model()


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(
            ASCIIUsernameValidator(),
        ),
        allow_null=False,
        allow_blank=False,
    )

    def validate_username(self, value):
        """
        "me" is not allowed as a username.
        """
        if value.lower() == 'me':
            message = f"Enter a valid username. '{value}' is not allowed."
            raise serializers.ValidationError(message)

        return value


class SignUpSerializer(UsernameSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        allow_null=False,
        allow_blank=False,
    )


class UserSerializer(SignUpSerializer, serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(
            ASCIIUsernameValidator(),
            UniqueValidator(queryset=User.objects.all()),
        ),
        allow_null=False,
        allow_blank=False,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        allow_null=False,
        allow_blank=False,
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User


class TokenSerializer(UsernameSerializer):
    confirmation_code = serializers.CharField(allow_blank=False)


class CategorуSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Categorу


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorуSerializer()
    rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        read_only_fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categorу.objects.all()
    )

    def validate_year(self, value):
        current_year = datetime.today().year
        if value > current_year:
            message = (
                'Нельзя добавлять произведения, которые еще не вышли.'
                f'Год выпуска {value} не может быть больше текущего.')
            raise serializers.ValidationError(message)
        return value

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        user = self.context['request'].user
        if self.context['request'].method == 'PATCH':
            return data
        if Review.objects.filter(
            title=title_id,
            author=user
        ).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв.')
        return data

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )
