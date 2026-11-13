
from django.contrib import admin
from .models import Category, Product, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("category", "is_active")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "sku",
        "size",
        "color",
        "cost_price",
        "selling_price",
        "is_active",
    )
    search_fields = ("product__name", "sku", "barcode")
    list_filter = ("size", "color", "is_active")
