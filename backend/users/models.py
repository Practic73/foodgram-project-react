from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True)
    username = models.CharField(' Логин', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscription',
        verbose_name='На кого подписались',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscription',
        verbose_name='Кто подписался',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
