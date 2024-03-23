from django.shortcuts import render
from rest_framework import status, viewsets


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    ...
