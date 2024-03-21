from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    username = models.CharField(
        verbose_name='Логин',
        max_length=256,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=256,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=256,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=256,
        blank=False
    )
    is_activ = models.BooleanField(
        verbose_name='Аккаунт активен',
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=256,
        blank=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
