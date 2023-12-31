from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
        'image',
        'cooking_time',
        'author',
        'pub_date',
        'in_favorite'
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    inlines = (RecipeIngredientInline, )

    def in_favorite(self, obj):
        return obj.favorites.all().count()


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients',
        'recipe',
        'amount',
    )


class Favoriteadmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, Favoriteadmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
