from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import CustomUserViewSet

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
