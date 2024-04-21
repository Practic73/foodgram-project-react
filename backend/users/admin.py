
from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email',)
    list_filter = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    empty_value_display = 'Не задано'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    list_filter = ('author', 'user')
    search_fields = ('author',)
    empty_value_display = 'Не задано'
