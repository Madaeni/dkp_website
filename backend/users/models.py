from django.contrib.auth.models import AbstractUser
from django.db import models


class Avatar(models.Model):
    avatar = models.FileField(
        upload_to='avatars/',
    )


class User(AbstractUser):
    avatar = models.ForeignKey(
        Avatar, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='user_avatar', verbose_name='Аватар'
    )
