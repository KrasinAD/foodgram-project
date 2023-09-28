import base64
import webcolors
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
# # from rest_framework.exceptions import ValidationError
# # from rest_framework.relations import SlugRelatedField
# # from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Ingredient, Tag, Recipe
from users.models import User

# # from django.contrib.auth.tokens import default_token_generator
# # from django.db.models import Avg
# # from django.shortcuts import get_object_or_404


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()
    # color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        # unique_together = ('name', 'color', 'slug')
    

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
    

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()


    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()
    
    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': (
                        'Убедитесь, что значение количества '
                        'ингредиента больше 0'
                    )
                })
        data['ingredients'] = ingredients
        return data
        


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для отображения рецептов в подписках."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
