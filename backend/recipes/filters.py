from django_filters.rest_framework import (FilterSet, filters,
                                           ModelMultipleChoiceFilter)

from .models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    author = filters.CharFilter(
        field_name='author__id',
    )
    tags = ModelMultipleChoiceFilter(
        to_field_name='slug',
        field_name='tags__slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, _, value):
        """Проверка наличия рецепта в избранном пользователя."""

        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _, value):
        """Проверка наличия рецепта в списке покупок пользователя."""

        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class TagFilter(FilterSet):

    class Meta:
        model = Tag
        fields = ('name', 'slug')
