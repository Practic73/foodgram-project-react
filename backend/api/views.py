from django.shortcuts import render
from rest_framework import status, viewsets


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    ...


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    ...


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    ...
