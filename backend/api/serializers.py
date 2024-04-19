import base64

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile


from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe, AmountIngredient)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeListSerializer(serializers.ModelSerializer):

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tag',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            )

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='temp.' + ext,
            )
        return super().to_internal_value(data)


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели соединяющей ингредиенты и рецепты"""

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = IngredientSerializer(many=True)
    tag = TagSerializer(many=True)

    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientToRecipeSerializer(
        many=True,)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tag',
            'image',
            'name',
            'text',
            'cooking_time',
            )


class RecipeDetailSerializer(serializers.ModelSerializer):

    tag = TagSerializer(many=True)
    ingredients = IngredientToRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    author = CustomUserSerializer()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tag',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
