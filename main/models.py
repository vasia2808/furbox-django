from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='categories_images', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ("id",)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2)
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='products')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        ordering = ('id',)
        indexes = [
            models.Index(fields=['date_added']),
            models.Index(fields=['category', 'date_added']),
        ]

    def __str__(self):
        return f'{self.name} Quantity - {self.quantity}'

    def get_absolute_url(self):
        return reverse("main:product", kwargs={"product_slug": self.slug})
    

    def display_id(self):
        return f'{self.id:05}'

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price*self.discount/100, 2)

        return self.price


class ProductImage(models.Model):
    image = models.ImageField(upload_to='products_images')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_images'
        ordering = ('id',)
