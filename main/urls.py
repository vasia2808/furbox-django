from django.urls import path
from main import views


app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('search/', views.CategoryView.as_view(), name='search'),
    path('catalog/<slug:category_slug>/', views.CategoryView.as_view(), name='category'),
    path('product/<slug:product_slug>/', views.ProductView.as_view(), name='product'),
]
