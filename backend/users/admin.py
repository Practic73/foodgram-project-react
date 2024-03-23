from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_activ')
    list_filter = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    empty_value_display = 'Не задано'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    list_filter = ('author', 'user')
    search_fields = ('author',)
    empty_value_display = 'Не задано'
