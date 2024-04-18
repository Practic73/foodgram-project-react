from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserSerializer):
    """
    Сериализатор для регистрации пользователей.
    """

    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return False


class SubscriptionsSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Subscription
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',
                  )

    def get_recipes(self, obj):
        random_mass = []
        return random_mass

    def get_recipes_count(self, obj):
        return 222

    def get_is_subscribed(self, obj):
        return False
