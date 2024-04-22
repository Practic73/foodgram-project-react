from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag)
from users.models import Subscribtion, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка наличия подписки."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientShortSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента с двумя полями - id и amount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount'
        )


class IngredientSerializer(IngredientShortSerializer):
    """Сериализатор количества ингредиента для рецептов."""

    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор одного ингредиента для страницы ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта."""

    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    author = CustomUserSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка наличия рецепта в избранном."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия рецепта в корзине."""

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeListSerializer(RecipeSerializer):
    """Сериализатор для списка рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для одного рецепта после создания."""

    ingredients = IngredientShortSerializer(
        many=True,
        source='recipe_ingredients'
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.ListField(required=True)
    ingredients = serializers.ListField(required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def check_ingredients(self, data):
        validated_items = []
        existed = []
        for item in data:
            ingredient = Ingredient.objects.get(pk=item['id']).name
            if ingredient in validated_items:
                existed.append(ingredient)
            validated_items.append(ingredient)
        if existed:
            raise serializers.ValidationError(
                'Ингредиенты уже добавлены в рецепт'
            )

    def validate(self, data):
        ingredients = data.get('ingredients')
        self.check_ingredients(ingredients)
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredient_data, recipe):
        ingredient = Ingredient.objects.get(pk=ingredient_data['id'])
        if ingredient_data['amount'] < 1:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 ингредиент.'
            )
        if not Ingredient.objects.filter(id=ingredient.id).exists():
            raise serializers.ValidationError(
                'Ингредиента не сущетсвует.'
            )
        RecipeIngredients.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=ingredient_data['amount']
        )
        return ingredient

    def create(self, validated_data):
        tags_list = []
        ingredient_list = []
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for id in tags:
            if id:
                tag = Tag.objects.get(id=id)
                tags_list.append(tag)
        for ingredient_data in ingredients:
            ingredient = self.create_ingredients(
                ingredient_data,
                recipe
            )
            ingredient_list.append(ingredient)
        recipe.tags.set(tags_list)
        recipe.ingredients.set(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        ingredient_list = []
        ingredients = validated_data.get('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(validated_data.get('tags', instance.tags))
        RecipeIngredients.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients:
            ingredient = self.create_ingredients(
                ingredient_data,
                instance
            )
            ingredient_list.append(ingredient)

        ingredient_list.append(ingredient)
        instance.ingredients.set(ingredient_list)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = RecipeListSerializer(instance, context=context)
        data = serializer.data
        data['is_favorited'] = serializer.get_is_favorited(instance)
        data['is_in_shopping_cart'] = serializer.get_is_in_shopping_cart(
            instance
        )
        return data

    def validate_tags(self, tags):
        tags_len = len(tags)
        if tags_len == 0:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 тег.'
            )
        if tags_len != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными.'
            )
        return tags


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        request = self.context.get('request')
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                queryset = queryset[:int(recipes_limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author_id=obj.id).count()
