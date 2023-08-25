from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    email = models.EmailField(
        max_length=255, unique=True, verbose_name="Почта"
    )

    REQUIRED_FIELDS = ["first_name", "last_name", "email"]


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="uq_user_author"
            )
        ]
