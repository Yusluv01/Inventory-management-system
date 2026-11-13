
from django.contrib import admin
from .models import StockLevel, StockMovement


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "quantity_on_hand",
        "reorder_level",
        "updated_at",
    )

    search_fields = (
        "variant__product__name",
        "variant__sku",
    )

    list_filter = ("updated_at",)

    readonly_fields = ("updated_at",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "movement_type",
        "quantity",
        "performed_by",
        "created_at",
    )

    search_fields = (
        "variant__product__name",
        "variant__sku",
        "reason",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    readonly_fields = (
        "variant",
        "movement_type",
        "quantity",
        "reason",
        "performed_by",
        "created_at",
    )
