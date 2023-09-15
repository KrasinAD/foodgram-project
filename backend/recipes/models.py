from foodgram.settings import NAME_LENGTH
from django.core.validators import MinValueValidator
from users.models import User

# from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# from .validators import validate_year


class Tag(models.Model):
    # BREAKFAST = 'завтрак'
    # LUNCH = 'обед'
    # DINNER = 'ужин'
    # COLOR_HEX = (
    #     (),
    #     (),
    #     (),
    # )
    name = models.CharField(
        'Название',
        max_length=NAME_LENGTH,
        # unique=True
    )
    # color = models.CharField(max_length=7, choices=CHOICES)
    slug = models.SlugField(
        'Уникальный слаг', 
        max_length=NAME_LENGTH, 
        # unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=NAME_LENGTH,  db_index=True)
    measurement_unit = models.CharField('Количество', max_length=NAME_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField('Название', max_length=NAME_LENGTH, db_index=True)
    text = models.TextField('Описание', blank=True, null=True)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)', 
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
        default=None
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Ingredient',
        related_name='ingredients',
        verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        through='Tag',
        related_name='tags',
        verbose_name='Тег'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_user_following'
            )
        ]
