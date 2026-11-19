from django.urls import path
from wishlists import views


app_name = 'wishlists'

urlpatterns = [
    path('wishlist_add/', views.WishlistAddView.as_view(), name='wishlist_add'),
    path('wishlist_remove/', views.WishlistRemoveView.as_view(), name='wishlist_remove'),
]
