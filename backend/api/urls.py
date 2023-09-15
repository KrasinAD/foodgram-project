from rest_framework.routers import DefaultRouter

from django.urls import include, path, re_path

from .views import (IngredientViewSet, TagViewSet)



app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
# router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
