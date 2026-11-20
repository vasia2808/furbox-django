from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from main.forms import ReviewForm
from main.models import Banner, Category, Product, Review
from main.utils import q_search
from wishlists.models import WishlistItem

from main.services import (
    get_bestsellers,
    get_new_items,
    get_recommendations,
    get_related_products
)


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        banners = Banner.objects.all()
        context['title'] = 'FurBox - Your Furry Shop'
        context['banners'] = banners
        context['recommended_products'] = get_recommendations(self.request.user)
        context['bestsellers'] = get_bestsellers()
        context['new_items'] = get_new_items()
        return context


class CatalogView(ListView):
    model = Category
    # queryset = Product.objects.all().order_by('-id')
    template_name = 'main/catalog.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Catalog - FurBox'
        return context


class CategoryView(ListView):
    model = Product
    # queryset = Product.objects.all().order_by('-id')
    template_name = 'main/category.html'
    context_object_name = 'products'
    paginate_by = 12
    #allow_empty = False

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        order_by = self.request.GET.get('order_by')
        query = self.request.GET.get('q')

        if query:
            products = q_search(query)
        else:
            products = super().get_queryset().filter(category__slug=category_slug)

        if order_by and order_by != 'default':
            products = products.order_by(order_by)
        
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.kwargs.get('category_slug')
        category_name = Category.objects.get(slug=category_slug).name if category_slug else 'Search'

        context['title'] = f'{category_name} - Furbox'
        context['category_name'] = category_name
        #context['slug_url'] = self.kwargs.get('category_slug')
        return context


class ProductView(DetailView):
    # model = Product
    # queryset = Product.objects.all()
    # slug_field = 'slug'
    template_name = 'main/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product = Product.objects.get(slug=self.kwargs.get(self.slug_url_kwarg))
        return product

    def get_context_data(self, **kwargs):
        product = self.object

        reviews = Review.objects.filter(
            product=product
        ).select_related('user').order_by('-created_timestamp')

        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

        user = self.request.user

        is_wished = False

        if user.is_authenticated:
            is_wished = WishlistItem.objects.filter(user=user, product=product).exists()

        paginator = Paginator(reviews, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = super().get_context_data(**kwargs)
        context['title'] = f'{product.name} - FurBox'
        context['reviews'] = page_obj
        context['average_rating'] = average_rating
        context['reviews_count'] = reviews.count()
        context['is_wished'] = is_wished
        context['page_obj'] = page_obj
        context['related_products'] = get_related_products(product)
        
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'main/review_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product,
            slug=kwargs['product_slug']
        )

        # Проверяем наличие завершённого заказа с товаром
        has_completed_order = self.product.order_items.filter(
            order__user=request.user,
            order__status='Completed'
        ).exists()

        if not has_completed_order:
            raise PermissionDenied

        # Проверяем, не оставлял ли пользователь отзыв
        if Review.objects.filter(
            user=request.user,
            product=self.product
        ).exists():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(
            slug=self.kwargs['product_slug']
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        product = Product.objects.get(slug=self.kwargs.get('product_slug'))
        
        context = super().get_context_data(**kwargs)
        context["product"] = product
        return context
    

    def get_success_url(self):
        return reverse(
            'main:product',
            kwargs={'product_slug': self.object.product.slug}
        ) + '#reviews'
