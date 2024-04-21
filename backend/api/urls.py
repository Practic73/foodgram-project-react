from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (TagViewSet, RecipeViewSet,
                    IngredientViewSet, UserListViewSet)

app_name = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserListViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]