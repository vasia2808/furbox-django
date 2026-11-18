from django.contrib import admin

from main.models import Banner, Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name"]


class ProductImageTabulareAdmin(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    ...


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "quantity", "price", "discount"]
    list_editable = ["discount"]
    search_fields = ["name", "description"]
    list_filter = ["discount", "quantity", "category"]
    fields = [
        "name",
        "category",
        "slug",
        "description",
        ("price", "discount"),
        "quantity",
        "date_added",
    ]

    readonly_fields = ("date_added",)

    inlines = (ProductImageTabulareAdmin,)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    ...
