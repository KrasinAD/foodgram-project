from djoser.serializers import UserSerializer
from rest_framework import serializers, status

from recipes.models import Recipe
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Кастомный серилизатор для User, добавляет строчку подписки."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()
 

# class FollowSerializer(serializers.ModelSerializer):
#     """Серилизатор User для подписок."""
#     email = serializers.ReadOnlyField(source='following.email')
#     id = serializers.ReadOnlyField(source='following.id')
#     username = serializers.ReadOnlyField(source='following.username')
#     first_name = serializers.ReadOnlyField(source='following.first_name')
#     last_name = serializers.ReadOnlyField(source='following.last_name')
#     is_subscribed = serializers.SerializerMethodField(read_only=True)
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Follow
#         fields = ('email', 'id', 'username', 'first_name', 'last_name',
#                   'is_subscribed', 'recipes', 'recipes_count')

#     def get_is_subscribed(self, obj):
#         # user = self.context.get('request').user
#         # if not user.is_anonymous:
#         #     return Follow.objects.filter(
#         #         user=user,
#         #         following=obj
#         #     ).exists()
#         # return False
#         return True

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         limit = request.query_params.get('recipes_limit')
#         recipes = Recipe.objects.filter(author=obj)
#         if limit and limit.isdigit():
#             recipes = recipes[:int(limit)]
#         return MiniRecipeSerializer(recipes, many=True).data

#     def get_recipes_count(self, obj):
#         return Recipe.objects.filter(author=obj).count()

class FollowListSerializer(serializers.ModelSerializer):
    """Серилизатор User для подписок."""
    # email = serializers.ReadOnlyField(source='following.email')
    # id = serializers.ReadOnlyField(source='following.id')
    # username = serializers.ReadOnlyField(source='following.username')
    # first_name = serializers.ReadOnlyField(source='following.first_name')
    # last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

        # user = self.context.get('request').user
        # if not request.user.is_anonymous:
        #     return Follow.objects.filter(
        #         user=request.user,
        #         following=obj
        #     ).exists()
        # return False
        # return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return MiniRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор подписки. """
    class Meta:
        model = Follow
        fields = ('user', 'following')

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.following,
            context={'request': self.context.get('request')}
        ).data
    
    def validate(self, data):
        user = self.context.get('request').user
        following = self.context.get('following')
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == following:
            raise serializers.ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return data


class MiniRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для отображения рецептов в подписках, избранном и 
    списке покупок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
