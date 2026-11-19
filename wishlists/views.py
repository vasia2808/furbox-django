from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from main.models import Product
from wishlists.models import WishlistItem


class WishlistAddView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        user = self.request.user

        _, created = WishlistItem.objects.get_or_create(product=product, user=user)

        response_data = {
            'message': 'Product added to wishlist' if created else 'Product is already in wishlist'
        }

        return JsonResponse(response_data)


class WishlistRemoveView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        user = self.request.user

        items = WishlistItem.objects.filter(product=product, user=user)

        is_deleted = False

        if items.exists():
            is_deleted = items.delete()

        response_data = {
            'message': 'Product removed from wishlist' if is_deleted else 'Product is not in wishlist'
        }

        return JsonResponse(response_data)
