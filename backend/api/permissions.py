from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = 'Изменение(удаление) чужого контента запрещено!'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )



# class UserSubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор пользователя в подписках"""
#     email = serializers.ReadOnlyField(source='following.email')
#     id = serializers.ReadOnlyField(source='following.id')
#     username = serializers.ReadOnlyField(source='following.username')
#     first_name = serializers.ReadOnlyField(source='following.first_name')
#     last_name = serializers.ReadOnlyField(source='following.last_name')
#     is_subscribed = serializers.SerializerMethodField(
#         method_name='get_is_subscribed'
#     )
#     recipes = serializers.SerializerMethodField(
#         method_name='get_recipes'
#     )
#     recipes_count = serializers.SerializerMethodField(
#         method_name='get_recipes_count'
#     )

#     class Meta:
#         model = Subscription
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name',
#             'is_subscribed', 'recipes', 'recipes_count'
#         )

#     def get_is_subscribed(self, obj):
#         return obj.user == self.context['request'].user

#     def get_recipes(self, obj):
#         request = self.context['request']
#         recipes_limit = request.query_params.get('recipes_limit')
#         if not recipes_limit:
#             recipes = obj.following.recipes.all()
#         else:
#             recipes = obj.following.recipes.all()[:int(recipes_limit)]
#         return RecipeInListSerializer(
#             recipes, many=True, read_only=True
#         ).data

#     def get_recipes_count(self, obj):
#         try:
#             return obj.recipes_count
#         except AttributeError:
#             return Recipe.objects.filter(
#                 author=obj.following
#             ).count()

#     def validate(self, data):

#         return data


# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор подписок"""
#     class Meta:
#         model = Subscription
#         fields = ('user', 'following')

#     def validate(self, data):
#         user = data['user']
#         following = data['following']
#         if user == following:
#             raise serializers.ValidationError(
#                 'Невозможно подписаться на самого себя')
#         action = self.context['action']
#         user_in_subscription = Subscription.objects.filter(
#             user=user,
#             following=following
#         )
#         if action == 'subscribe':
#             if user_in_subscription:
#                 raise serializers.ValidationError(
#                     'Вы уже подписаны на этого пользователя')
#         elif action == 'unsubscribe':
#             if not user_in_subscription:
#                 raise serializers.ValidationError(
#                     'Данного пользователя нет в подписках')
#             user_in_subscription.delete()
#         return data

#     def to_representation(self, value):
#         serializer = UserSubscriptionSerializer(value, context=self.context)
#         return serializer.data


# class SubscriptionViewSet(UserViewSet):
#     """Вьюсет подписок"""
#     @action(
#         methods=['GET'],
#         detail=False,
#         filter_backends=[DjangoFilterBackend],
#         permission_classes=[IsAuthenticated]
#     )
#     def subscriptions(self, request):
#         """Метод получения списка авторов в подписках"""
#         follower_queryset = request.user.follower.all()
#         paginated_queryset = self.paginate_queryset(follower_queryset)
#         serializer = UserSubscriptionSerializer(
#             paginated_queryset,
#             many=True,
#             context={'request': self.request}
#         )
#         return self.get_paginated_response(serializer.data)

#     @action(
#         methods=['POST'],
#         detail=True,
#         permission_classes=[IsAuthenticated]
#     )
#     def subscribe(self, request, id):
#         """Метод подписки на автора"""
#         serializer = SubscriptionSerializer(
#             data={'following': id, 'user': request.user.id},
#             context={'request': self.request, 'action': 'subscribe'}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user)
#         return response.Response(
#             serializer.data, status=status.HTTP_201_CREATED
#         )

#     @subscribe.mapping.delete
#     def subscribe_delete(self, request, id):
#         """Метод отписки от автора"""
#         get_object_or_404(User, pk=id)
#         serializer = SubscriptionSerializer(
#             data={'following': id, 'user': request.user.id},
#             context={'request': self.request, 'action': 'unsubscribe'}
#         )
#         serializer.is_valid(raise_exception=True)
#         return response.Response(status=status.HTTP_204_NO_CONTENT)
    

# class CustomUserViewSet(UserViewSet):
#     """ViewSet для пользователей."""

#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#     pagination_class = CustomPagination

#     @action(
#         detail=False,
#         methods=['GET'],
#         permission_classes=[IsAuthenticated],
#         serializer_class=SubscriptionSerializer
#     )
#     def subscriptions(self, request):
#         user = request.user
#         favorites = user.followers.all()
#         users_id = [favorite_instance.author.id for favorite_instance in favorites]
#         users = User.objects.filter(id__in=users_id)
#         paginated_queryset = self.paginate_queryset(users)
#         serializer = self.serializer_class(paginated_queryset, many=True)
#         return self.get_paginated_response(serializer.data)

#     @action(
#         detail=True,
#         methods=('post', 'delete'),
#         serializer_class=SubscriptionSerializer
#     )
#     def subscribe(self, request, id=None):
#         user = request.user
#         author = get_object_or_404(User, pk=id)

#         follow_search = Follow.objects.filter(user=user, author=author)

#         if request.method == 'POST':
#             if user == author:
#                 raise exceptions.ValidationError('Подписываться на себя запрещено.')
#             if follow_search.exists():
#                 raise exceptions.ValidationError('Вы уже подписаны на этого пользователя.')
#             Follow.objects.create(user=user, author=author)
#             serializer = self.get_serializer(author)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             if not follow_search.exists():
#                 raise exceptions.ValidationError('Вы не подписаны на этого пользователя.')
#             Follow.objects.filter(user=user, author=author).delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)


# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     http_method_names = ('get', 'post', 'patch', 'delete')
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = RecipeFilter
#     pagination_class = CustomPagination
#     permission_classes = (AuthorOrReadOnly,)

#     def get_serializer_class(self):
#         if self.request.method in permissions.SAFE_METHODS:
#             return RecipeSerializer
#         return RecipeWriteSerializer

#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=[permissions.IsAuthenticated]
#     )
#     def favorite(self, request, pk):
#         if request.method == 'POST':
#             return add_to(self, Favorite, request.user, pk)
#         return delete_from(self, Favorite, request.user, pk)

#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=[permissions.IsAuthenticated]
#     )
#     def shopping_cart(self, request, pk):
#         if request.method == 'POST':
#             return add_to(self, ShoppingCart, request.user, pk)
#         return delete_from(self, ShoppingCart, request.user, pk)
    


# def add_to(self, model, user, pk):
#     if model.objects.filter(user=user, recipe__id=pk).exists():
#         return Response({'error': 'Уже существует'},
#                         status=status.HTTP_400_BAD_REQUEST)
#     recipe = get_object_or_404(Recipe, pk=pk)
#     instance = model.objects.create(user=user, recipe=recipe)
#     serializer = FavoriteSerializer(instance)
#     return Response(data=serializer.data, status=status.HTTP_201_CREATED)


# def delete_from(self, model, user, pk):
#     if model.objects.filter(user=user, recipe__id=pk).exists():
#         model.objects.filter(
#             user=user, recipe__id=pk
#         ).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     return Response(status=status.HTTP_400_BAD_REQUEST)