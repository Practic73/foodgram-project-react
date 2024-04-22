from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import RecipeShortSerializer
from recipes.models import Recipe


def add_recipe(self, request, pk, model):
    recipe = get_object_or_404(Recipe, id=pk)

    if model.objects.filter(
            recipe=recipe,
            user=request.user,
    ).exists():
        return Response(status=HTTPStatus.BAD_REQUEST)
    model.objects.create(recipe=recipe, user=request.user)
    serializer = RecipeShortSerializer(recipe)

    if recipe is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(data=serializer.data, status=HTTPStatus.CREATED)


def delete_recipe(self, request, pk, model):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(
            user=request.user,
            recipe=recipe,
    ).exists():
        model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(status=HTTPStatus.BAD_REQUEST)
