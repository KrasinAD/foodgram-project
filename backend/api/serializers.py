import webcolors
from rest_framework import serializers
# # from rest_framework.exceptions import ValidationError
# # from rest_framework.relations import SlugRelatedField
# # from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Follow, Ingredient, Tag #, Recipe
from users.models import User

# # from django.contrib.auth.tokens import default_token_generator
# # from django.db.models import Avg
# # from django.shortcuts import get_object_or_404


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'email', 'username', 'first_name', 'last_name', 'password'
#         )

class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()
    # color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        unique_together = ('name', 'color', 'slug')
        


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        


# class RecipeSerializer(serializers.ModelSerializer):

#     class Meta:
#         fields = ('name', 'measurement_unit')
#         model = Ingredient


# class FollowSerializer(serializers.ModelSerializer):
#     user = serializers.SlugRelatedField(
#         queryset=User.objects.all(),
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     following = serializers.SlugRelatedField(
#         queryset=User.objects.all(),
#         slug_field='username'
#     )

#     class Meta:
#         model = Follow
#         fields = ('user', 'following')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=['user', 'following']
#             )
#         ]

#     def validate(self, data):
#         if data['following'] == data['user']:
#             raise serializers.ValidationError(
#                 'Нельзя подписываться на себя.')
#         return data