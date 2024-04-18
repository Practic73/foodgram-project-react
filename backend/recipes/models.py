from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=256,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return (f'Ингредиент: {self.name} единица измерения: '
                f'{self.measurement_unit}.')


class Recipe(models.Model):
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Список ингредиентов',
        through='AmountIngredient',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        'Описание',
        max_length=256,
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Блюдо: {self.name} автор: {self.author}'


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amountIngredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='amountIngredient',
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'Ингредиент: {self.ingredient} количество: {self.amount}'


class Favorite(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe} добавлен в избранные пользователем {self.user}'


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Список покупок пользователя: {self.user}'
