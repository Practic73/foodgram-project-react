from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from api.paginations import CustomPagePagination
from .serializers import (
    CustomUserSerializer,
    SubscriptionsSerializer,
    CustomUserCreateSerializer)
from .models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagePagination
    serializer_class = CustomUserSerializer

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    """ def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        else:
            return CustomUserSerializer """

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        author = request.user
        subscriptions = Subscription.objects.filter(author=author)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        current_subscripes = Subscription.objects.filter(
                                    author=author, user=user).exists()
        if request.method == 'POST':
            if (author.id == request.user.id) or (current_subscripes):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(author=author, user=request.user)
            follows = User.objects.filter(id=id).first()
            serializer = SubscriptionsSerializer(
                follows,
                context={'request': request},
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            User.objects.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

