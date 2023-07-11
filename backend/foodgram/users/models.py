from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_username


class User(AbstractUser):
    '''Модель пользователей.'''

    USER = 'user'
    ADMIN = 'admin'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    )

    username = models.CharField(
        max_length=150,
        blank=True,
        validators=(validate_username,),
        verbose_name='Юзернейм пользователя',
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Адрес эл.почты пользователя'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль в системе'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписчиков.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
