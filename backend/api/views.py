from django.shortcuts import render
from rest_framework import status, viewsets
from djoser.views import UserViewSet
from users.models import  Subscription, User
from .serializers import UserSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    ...


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    ...


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    ...


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        # permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)