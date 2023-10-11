import base64
import webcolors
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
# # from rest_framework.exceptions import ValidationError
# # from rest_framework.relations import SlugRelatedField
# # from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Ingredient, IngredientRecipe, Favorite, Recipe, ShoppingCart, Tag 
# from users.models import User
from users.serializers import CustomUserSerializer


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

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
   

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
        id = serializers.ReadOnlyField(source='ingredients.id')
        name = serializers.ReadOnlyField(source='ingredients.name')
        measurement_unit = serializers.ReadOnlyField(
            source='ingredients.measurement_unit'
        )

        class Meta:
            model = IngredientRecipe
            fields = ('id', 'name', 'measurement_unit', 'amount')

#######
class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количесто ингредиента не может быть отрицательным'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()


class RecipeCreationSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time' 
        )

    # def add_ingredients(self, ingredients_list, recipe):
    #     IngredientRecipe.objects.bulk_create([
    #         IngredientRecipe(
    #             recipe=recipe,
    #             ingredient_id=ingredient.get('id'),
    #             amount=ingredient.get('amount'),
    #         ) for ingredient in ingredients_list
    #     ])

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.add(*tags)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            ) 
        # self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        IngredientRecipe.objects.filter(recipe_id=instance.pk).delete()
        lst = []
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)
        instance.save()
        # self.add_ingredients(ingredients, instance)
        # super().update(instance, validated_data)
        return instance

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


# class MiniRecipeSerializer(serializers.ModelSerializer):
#     """Серилизатор для отображения рецептов в подписках, избранном и 
#     списке покупок."""

#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')

#     def create(self, validated_data):
#         if 'ingredients' not in self.initial_data:
#             recipe = Recipe.objects.create(**validated_data)
#             return recipe
#         ingredients = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(**validated_data)
#         for ingredient in ingredients:
#             current_ingredient, status = Ingredient.objects.get_or_create(
#                 **ingredient
#             )
#             IngredientRecipe.objects.create(
#                 ingredient=current_ingredient, recipe=recipe
#             )
#         return recipe

#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.color = validated_data.get('color', instance.color)
#         instance.birth_year = validated_data.get(
#             'birth_year', instance.birth_year
#         )
#         instance.image = validated_data.get('image', instance.image)

#         if 'achievements' not in validated_data:
#             instance.save()
#             return instance

#         achievements_data = validated_data.pop('achievements')
#         lst = []
#         for achievement in achievements_data:
#             current_achievement, status = Achievement.objects.get_or_create(
#                 **achievement
#             )
#             lst.append(current_achievement)
#         instance.achievements.set(lst)

#         instance.save()
#         return instance
# #      
#     def add_tags_ingredients(self, ingredients, tags, model):
#         for ingredient in ingredients:
#             IngredientRecipe.objects.update_or_create(
#                 recipe=model,
#                 ingredient=ingredient['id'],
#                 amount=ingredient['amount'])
#         model.tags.set(tags)

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = super().create(validated_data)
    #     self.add_tags_ingredients(ingredients, tags, recipe)
    #     return recipe

    # def update(self, instance, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     instance.ingredients.clear()
    #     self.add_tags_ingredients(ingredients, tags, instance)
    #     return super().update(instance, validated_data)
    

    # def create(self, validated_data):
    #     image = validated_data.pop('image')
    #     ingredients_data = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(image=image, **validated_data)
    #     tags_data = self.initial_data.get('tags')
    #     recipe.tags.set(tags_data)
    #     self.create_ingredients(ingredients_data, recipe)
    #     return recipe

    # def update(self, instance, validated_data):
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time', instance.cooking_time
    #     )
    #     instance.tags.clear()
    #     tags_data = self.initial_data.get('tags')
    #     instance.tags.set(tags_data)
    #     IngredientAmount.objects.filter(recipe=instance).all().delete()
    #     self.create_ingredients(validated_data.get('ingredients'), instance)
    #     instance.save()
    #     return instance



