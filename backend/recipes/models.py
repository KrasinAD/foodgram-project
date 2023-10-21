from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

MIN_VALUE = 1
MAX_VALUE = 3200


class Tag(models.Model):
    """ Модель Тегов. """
    name = models.CharField(
        'Название',
        max_length=200,
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
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиентов. """
    name = models.CharField(
        'Название',
        max_length=200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель рецептов. """
    name = models.CharField(
        'Название',
        max_length=200,
    )
    text = models.TextField(
        'Описание',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(MIN_VALUE, 'Минимальное время приготовления.'),
            MaxValueValidator(MAX_VALUE, 'Максимальное время приготовления.')
        ]
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
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Промежуточная модель связи игредиентов и рецептов."""
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE, 'Минимальное количество ингредиента в рецепте.'
            ),
            MaxValueValidator(
                MAX_VALUE, 'Максимальное количество ингредиента в рецепте.'
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='unique_ingredients_recipe'
            )
        ]

    def __str__(self):
        return (f'{self.ingredients.name} в количестве {self.amount} '
                f'{self.ingredients.measurement_unit} для {self.recipe.name}')


class Favorite(models.Model):
    """ Модель избранных рецептов. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное.'


class ShoppingCart(models.Model):
    """ Модель списка покупок. """
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
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'В списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок.'
