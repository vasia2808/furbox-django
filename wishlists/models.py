from django.db import models

from main.models import Product
from users.models import User


class WishlistItem(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'wishlist_items'
        ordering = ("id",)
