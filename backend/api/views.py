from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import CustomPagePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CustomUserSerializer, IngredientDetailSerializer, RecipeCreateSerializer,
    RecipeListSerializer, RecipeSerializer, RecipeSerializerShort,
    SubscriptionListSerializer, TagSerializer)
from recipes.filters import IngredientFilter, RecipeFilter, TagFilter
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag)
from utils import views_utils
from users.models import Follow, User


class UserListViewSet(views.UserViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
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
        methods=('GET', 'PATCH'),
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
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        author = request.user
        limit = request.query_params.get('limit')
        if limit:
            subscriptions = Follow.objects.filter(author=author)[:int(limit)]
        else:
            subscriptions = Follow.objects.filter(author=author)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        current_subscriptions = Follow.objects.filter(
            user=user, author=author)
        if user == author:
            content = {'error': 'подписываться на самого себя нельзя.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            if current_subscriptions.exists():
                content = {'error': 'такая подписка уже существует.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=request.user, author=author)
            follows = get_object_or_404(User, id=id)
            serializer = SubscriptionListSerializer(
                follows,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if user != author:
            if current_subscriptions.exists():
                current_subscriptions.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filterset_class = TagFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientDetailSerializer
    search_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagePagination

    def get_serializer_class(self):
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
