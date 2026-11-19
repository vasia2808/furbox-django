from django.core.paginator import Paginator
from django.db.models import Avg
from django.views.generic import DetailView, ListView, TemplateView

from main.models import Banner, Category, Product, Review
from main.utils import q_search
from wishlists.models import WishlistItem


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        banners = Banner.objects.all()
        context['title'] = 'FurBox - Your Furry Shop'
        context['banners'] = banners
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

        paginator = Paginator(reviews, 4)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = super().get_context_data(**kwargs)
        context['title'] = f'{product.name} - FurBox'
        context['reviews'] = page_obj
        context['average_rating'] = average_rating
        context['reviews_count'] = reviews.count()
        context['is_wished'] = is_wished
        context['page_obj'] = page_obj
        
        return context
