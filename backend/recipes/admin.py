from django.contrib import admin
from .models import (Ingredient, Tag, Recipe,
                     ShoppingCart, Favorite, RecipeIngredient)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3
    min_num = 1


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tag.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites')
    list_filter = ('author', 'name', 'tag')
    search_fields = ('name', 'author', 'tag')
    inlines = (IngredientInline, RecipeTagsInLine)
    empty_value_display = 'Не задано'

    def get_favorites(self, obj):
        return obj.favorite.count()
    get_favorites.short_description = 'Добавлено в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    list_filter = ('name',)
    search_fields = ('name', )
    empty_value_display = 'Не задано'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'author')
    list_filter = ('recipe', 'author')
    search_fields = ('author', )
    empty_value_display = 'Не задано'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
    list_filter = ('author', 'recipe')
    search_fields = ('author', 'recipe')
    empty_value_display = 'Не задано'
