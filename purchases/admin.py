from django.contrib import admin
from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

    readonly_fields = ("quantity_received",)
    

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "supplier",
        "status",
        "expected_date",
        "created_at",
    )

    search_fields = (
        "reference",
        "supplier__name",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):

    list_display = (
        "purchase",
        "variant",
        "quantity_ordered",
        "quantity_received",
        "unit_cost",
    )

    search_fields = (
        "purchase__reference",
        "variant__sku",
        "variant__product__name",
    )

    readonly_fields = (
        "quantity_received",
    )
