from datetime import timedelta

from django.db.models import Sum, Count, Case, When, IntegerField
from django.utils import timezone

from main.models import Product
from orders.models import OrderItem


def valid_sales():
    return OrderItem.objects.filter(
        order__is_paid=True
    ).exclude(
        order__status__in=['Cancelled', 'Canceled', 'Refunded']
    ).filter(
        product__isnull=False
    )


def get_bestsellers(limit=8):
    week_ago = timezone.now() - timedelta(days=7)

    sales = valid_sales().filter(
        order__created_timestamp__gte=week_ago
    ).values(
        'product'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')

    product_ids = list(
        sales.values_list('product', flat=True)[:limit]
    )

    preserved_order = Case(
        *[
            When(pk=pk, then=position)
            for position, pk in enumerate(product_ids)
        ],
        output_field=IntegerField()
    )

    return Product.objects.filter(
        pk__in=product_ids,
        quantity__gt=0
    ).order_by(preserved_order)


def get_new_items(limit=8):
    return Product.objects.filter(
        quantity__gt=0
    ).order_by('-date_added')[:limit]


def get_recommendations(user, limit=8):
    if not user.is_authenticated:
        return None

    orders = valid_sales().filter(
        order__user=user
    )

    # Категории, отсортированные по количеству покупок
    category_ids = list(
        orders.values(
            'product__category_id'
        ).annotate(
            total=Sum('quantity')
        ).order_by(
            '-total'
        ).values_list(
            'product__category_id',
            flat=True
        )
    )

    if not category_ids:
        return None

    # Товары, которые пользователь уже покупал
    purchased_ids = orders.values_list(
        'product_id',
        flat=True
    ).distinct()

    # Приоритет категорий
    category_order = Case(
        *[
            When(category_id=category_id, then=position)
            for position, category_id in enumerate(category_ids)
        ],
        output_field=IntegerField()
    )

    return Product.objects.filter(
        category_id__in=category_ids,
        quantity__gt=0
    ).exclude(
        pk__in=purchased_ids
    ).order_by(
        category_order,
        '-date_added'
    )[:limit]


def get_related_products(product, limit=8):
    return Product.objects.filter(
        category=product.category,
        quantity__gt=0
    ).exclude(
        pk=product.pk
    ).order_by('-date_added')[:limit]
