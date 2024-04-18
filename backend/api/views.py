
from rest_framework import viewsets, permissions, filters
from django_filters import ModelMultipleChoiceFilter

from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    NumberFilter,
    BooleanFilter,
    AllValuesMultipleFilter,
    )
from api.paginations import CustomPagePagination
from recipes.models import Tag, Ingredient, Recipe
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateSerializer,
    RecipeDetailSerializer
    )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get',)
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name')


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов.
    """
    is_favorited = BooleanFilter(
        field_name='is_favorited',
        method='favorite_filter'
    )
    is_in_shopping_cart = BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    tags = AllValuesMultipleFilter(field_name='tag__slug')

    def favorite_filter(self, queryset, name, value):
        return Recipe.objects.filter(favorite__user=self.request.user)

    def shopping_cart_filter(self, queryset, name, value):
        return Recipe.objects.filter(shopping_cart__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ['author']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagePagination
    # filter_backends = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeDetailSerializer
