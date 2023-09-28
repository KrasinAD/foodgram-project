from foodgram.settings import NAME_LENGTH
from django.core.validators import MinValueValidator
from users.models import User

from django.db import models


class Tag(models.Model):
    """Модель Тега"""
    name = models.CharField(
        'Название',
        max_length=NAME_LENGTH,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=NAME_LENGTH,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        'Название',
        max_length=NAME_LENGTH,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Количество',
        max_length=NAME_LENGTH
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель рецептов"""
    name = models.CharField(
        'Название',
        max_length=NAME_LENGTH,
        db_index=True,
    )
    text = models.TextField(
        'Описание',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        null=True,
        default=None,
    )
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
        default=None,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingredients',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тег'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe'
            )
        ]


class IngredientRecipe(models.Model):
    """Промежуточная модель связи игредиентов и рецептов."""
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Минимальное количество')],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='unique_ingredients_recipe'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        # ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        # ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'В списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping'
            )
        ]
