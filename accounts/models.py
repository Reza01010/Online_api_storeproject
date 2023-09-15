from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    Seller = models.BooleanField(default=False)

    favorites = models.ManyToManyField('products.Product', through='products.UserFavorite', blank=True)




