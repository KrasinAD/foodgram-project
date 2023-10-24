import base64
import webcolors
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status

from recipes.models import (MAX_VALUE, MIN_VALUE, Favorite, Ingredient,
                            IngredientRecipe, Recipe, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer, MiniRecipeSerializer


class Hex2NameColor(serializers.Field):
    """Перевод цвета из HEX в название. """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    """ Расшифровка картинки из Base64. """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингидиентов. """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор на создание ингидиентов. """
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """ Сериализатор на указание колличества ингидиентов. """
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(
        required=True,
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
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор только для просмотра рецептов."""
    tags = TagSerializer(many=True,)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredients_recipe'
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj.id).exists()


class RecipeCreationSerializer(serializers.ModelSerializer):
    """Серилизатор на создание, редактирование и удаление рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientAmountSerializer(many=True, required=True,)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE, 'Минимальное время приготовления.'),
            MaxValueValidator(MAX_VALUE, 'Максимальное время приготовления.')
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name', 'text',
            'cooking_time',
        )

    def add_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            ingredient_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=ingredient['amount']
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.add(*tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        instance.ingredients.clear()
        self.add_ingredients(ingredients=ingredients, recipe=instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужен хоть один тег для рецепта'})
        ingredient_multitude = set()
        for ingredient_item in ingredients:
            if not Ingredient.objects.filter(pk=ingredient_item['id']):
                raise serializers.ValidationError(
                    f'Ингредиента {ingredient_item["id"]} не существует!'
                )
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_multitude:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранного. """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return MiniRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        if request.user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для списка покупок. """
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return MiniRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        request = self.context['request']
        if request.user.shopping_cart.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в список покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return data
