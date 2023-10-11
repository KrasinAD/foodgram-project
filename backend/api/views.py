
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
# from rest_framework.filters import SearchFilter
# from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from recipes.models import Ingredient, IngredientRecipe, Favorite, Recipe, ShoppingCart, Tag

from django.shortcuts import HttpResponse, get_object_or_404

# from .filters import TitlesFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer, TagSerializer,
                          RecipeCreationSerializer)
from users.serializers import MiniRecipeSerializer
from .pagination import CustomPagination


class ListRetrieveViewSet(mixins.ListModelMixin, 
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    # filter_backends = (SearchFilter,)
    # search_fields = ('name',)
    serializer_class = IngredientSerializer
    # pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    # lookup_field = 'slug'

class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags',)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreationSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(self, Favorite, request.user, pk)
            # if model.objects.filter(user=user, recipe__id=pk).exists():
            # return Response({'error': 'Уже существует'},
            #                 status=status.HTTP_400_BAD_REQUEST)
            # recipe = get_object_or_404(Recipe, pk=pk)
            # instance = model.objects.create(user=user, recipe=recipe)
            # serializer = FavoriteSerializer(instance)
            # return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return self.delete_from(self, Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(self, ShoppingCart, request.user, pk)
        return self.delete_from(self, ShoppingCart, request.user, pk)  

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'error': 'Уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.create(user=user, recipe=recipe)
        serializer = MiniRecipeSerializer(instance)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            model.objects.filter(
                user=user, recipe__id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
            """Отправка файла со списком покупок."""
            ingredients = IngredientRecipe.objects.filter(
                recipe__carts__user=request.user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(ingredient_amount=Sum('amount'))
            shopping_list = ['Список покупок:\n']
            for ingredient in ingredients:
                name = ingredient['ingredient__name']
                unit = ingredient['ingredient__measurement_unit']
                amount = ingredient['ingredient_amount']
                shopping_list.append(f'\n{name} - {amount}, {unit}')
            response = HttpResponse(shopping_list, content_type='text/plain')
            response['Content-Disposition'] = \
                'attachment; filename="shopping_cart.txt"'
            return response

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )
    # def favorite(self, request, *args, **kwargs):
    #     """
    #     Получить / Добавить / Удалить  рецепт
    #     из избранного у текущего пользоватля.
    #     """
    #     recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
    #     user = self.request.user
    #     if request.method == 'POST':
    #         if Favorite.objects.filter(author=user,
    #                                    recipe=recipe).exists():
    #             return Response({'errors': 'Рецепт уже добавлен!'},
    #                             status=status.HTTP_400_BAD_REQUEST)
    #         serializer = FavoriteSerializer(data=request.data)
    #         if serializer.is_valid(raise_exception=True):
    #             serializer.save(author=user, recipe=recipe)
    #             return Response(serializer.data,
    #                             status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     if not Favorite.objects.filter(author=user,
    #                                    recipe=recipe).exists():
    #         return Response({'errors': 'Объект не найден'},
    #                         status=status.HTTP_404_NOT_FOUND)
    #     Favorite.objects.get(recipe=recipe).delete()
    #     return Response('Рецепт успешно удалён из избранного.',
    #                     status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )


    
    # def shopping_cart(self, request, **kwargs):
    #     """
    #     Получить / Добавить / Удалить  рецепт
    #     из списка покупок у текущего пользоватля.
    #     """
    #     recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
    #     user = self.request.user
    #     if request.method == 'POST':
    #         if ShoppingCart.objects.filter(author=user,
    #                                        recipe=recipe).exists():
    #             return Response({'errors': 'Рецепт уже добавлен!'},
    #                             status=status.HTTP_400_BAD_REQUEST)
    #         serializer = ShoppingCartSerializer(data=request.data)
    #         if serializer.is_valid(raise_exception=True):
    #             serializer.save(author=user, recipe=recipe)
    #             return Response(serializer.data,
    #                             status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     if not ShoppingCart.objects.filter(author=user,
    #                                        recipe=recipe).exists():
    #         return Response({'errors': 'Объект не найден'},
    #                         status=status.HTTP_404_NOT_FOUND)
    #     ShoppingCart.objects.get(recipe=recipe).delete()
    #     return Response('Рецепт успешно удалён из списка покупок.',
    #                     status=status.HTTP_204_NO_CONTENT)

#     @action(detail=False,
#             methods=['get'],
#             permission_classes=[IsAuthenticated])
#     def download_shopping_cart(self, request):
#         """
#         Скачать список покупок для выбранных рецептов,
#         данные суммируются.
#         """
#         author = User.objects.get(id=self.request.user.pk)
#         if author.shopping_cart.exists():
#             return shopping_cart(self, request, author)
#         return Response('Список покупок пуст.',
#                         status=status.HTTP_404_NOT_FOUND)
    
# # использовать его выгрузка файлов





#####
    # @action(
    #   detail=False, 
    #   methods=['GET'], 
    #   permission_classes=[IsAuthenticated]
    # )
    # def download_shopping_cart(self, request):
    #     shopping_cart = ShoppingCart.objects.filter(user=request.user)
    #     recipes_id = [item.recipe.id for item in shopping_cart]
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__in=recipes_id).values('ingredient__name', 'ingredient__measurement_unit'
    #                                     ).annotate(amount=Sum('amount'))
    #     final_list = 'Список покупок от Foodgram\n\n'

    #     for item in ingredients:
    #         ingredient_name = item['ingredient__name']
    #         measurement_unit = item['ingredient__measurement_unit']
    #         amount = item['amount']
    #         final_list += f'{ingredient_name} ({measurement_unit}) {amount}\n'

    #     filename = 'foodgram_shopping_list.txt'
    #     response = HttpResponse(final_list[:-1], content_type='text/plain')
    #     response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    #     return response
    

    # @action(detail=True, methods=['get', 'delete'],
    #         permission_classes=[IsAuthenticated])
    # def favorite(self, request, pk=None):
    #     if request.method == 'GET':
    #         return self.add_obj(Favorite, request.user, pk)
    #     elif request.method == 'DELETE':
    #         return self.delete_obj(Favorite, request.user, pk)
    #     return None

    # @action(detail=True, methods=['get', 'delete'],
    #         permission_classes=[IsAuthenticated])
    # def shopping_cart(self, request, pk=None):
    #     if request.method == 'GET':
    #         return self.add_obj(Cart, request.user, pk)
    #     elif request.method == 'DELETE':
    #         return self.delete_obj(Cart, request.user, pk)
    #     return None
    

    # def add_obj(self, model, user, pk):
    #     if model.objects.filter(user=user, recipe__id=pk).exists():
    #         return Response({
    #             'errors': 'Рецепт уже добавлен в список'
    #         }, status=status.HTTP_400_BAD_REQUEST)
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     model.objects.create(user=user, recipe=recipe)
    #     serializer = CropRecipeSerializer(recipe)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete_obj(self, model, user, pk):
    #     obj = model.objects.filter(user=user, recipe__id=pk)
    #     if obj.exists():
    #         obj.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response({
    #         'errors': 'Рецепт уже удален'
    #     }, status=status.HTTP_400_BAD_REQUEST)