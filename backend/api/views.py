
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from recipes.models import Ingredient, Recipe, Tag
from users.models import User

from django.shortcuts import get_object_or_404

# from .filters import TitlesFilter
# from .permissions import (IsAdmin, IsAdminOrReadOnly,
#                           IsAuthorModerAdminOrReadOnly)
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class ListRetrieveViewSet(mixins.ListModelMixin, 
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    # filter_backends = (SearchFilter,)
    # search_fields = ('name',)
    serializer_class = TagSerializer
    # pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    # lookup_field = 'slug'


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
    serializer_class = RecipeSerializer