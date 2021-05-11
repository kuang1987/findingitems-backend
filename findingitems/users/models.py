from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class AuthUser(AbstractUser):
    wechat_openid = models.CharField(
        max_length=128,
        unique=True
    )
    wechat_unionid = models.CharField(
        max_length=128,
        unique=True
    )
    real_name = models.CharField(
        max_length=128,
        null=True
    )
    avatar_url = models.CharField(
        max_length=1024,
        null=True
    )

    def get_profile(self):
        return getattr(self, 'profile', None)


class UserSettings(models.Model):
    user = models.OneToOneField(
        'users.AuthUser',
        related_name='profile',
        on_delete=models.CASCADE,
    )
    default_loc = models.ForeignKey(
        'location.Location',
        related_name='set_default_by_user',
        on_delete=models.SET_NULL,
        null=True,
    )
