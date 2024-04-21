from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from api.paginations import CustomPagePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientDetailSerializer, RecipeCreateSerializer, RecipeListSerializer,
    RecipeSerializer, RecipeSerializerShort, TagSerializer)
from recipes.filters import IngredientFilter, RecipeFilter, TagFilter
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag)
from utils import views_utils


""" class UserListViewSet(views.UserViewSet):

    queryset = User.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ThisUserOrAdmin
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    @action(
        detail=False,
        url_path='subscriptions',
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):

        authors = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result_page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionListSerializer(
            result_page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):

        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user != author and not Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.create(user=request.user, author=author)
                follows = User.objects.filter(id=id).first()
                serializer = SubscriptionListSerializer(
                    follows,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': text_constants.SUBSCRIPTION_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user != author and Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': text_constants.NO_ENTRY},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        url_path='me',
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):

        if request.method == 'GET':
            serializer = CustomUserSerializer(
                request.user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK) """


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filterset_class = TagFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientDetailSerializer
    search_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagePagination

    def get_serializer_class(self):
        """Выбор сериализатора рецептов."""

        if self.action in ('list', 'retrive'):
            return RecipeListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное, удаление из избранного."""

        return views_utils.favorite(
            self,
            request,
            pk,
            Favorite,
            Recipe,
            RecipeSerializerShort
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок, удаление из списка покупок."""

        return views_utils.favorite(
            self,
            request,
            pk,
            ShoppingCart,
            Recipe,
            RecipeSerializerShort
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание txt-файла списка покупок."""

        shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).values_list('recipe_id', flat=True)

        ingredients = RecipeIngredients.objects.filter(
            recipe_id__in=shopping_cart
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')

        shopping_list_content = []

        for ingredient in ingredients:
            shopping_list_content.append(
                f'{ingredient["ingredient__name"]}:'
                + f' {ingredient["ingredient__measurement_unit"]},'
                + f' {ingredient["amount"]}\n'
            )

        shopping_list_string = ''.join(shopping_list_content)
        filename = 'shopping_list.txt'

        response = HttpResponse(
            shopping_list_string, content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
