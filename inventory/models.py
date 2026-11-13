
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class StockLevel(models.Model):
    variant = models.OneToOneField(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="stock_level"
    )

    quantity_on_hand = models.PositiveIntegerField(default=0)

    reorder_level = models.PositiveIntegerField(default=5)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["variant__product__name"]

    def __str__(self):
        return f"{self.variant} - {self.quantity_on_hand} units"


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ("OPENING", "Opening Stock"),
        ("PURCHASE", "Purchase"),
        ("SALE", "Sale"),
        ("RETURN", "Customer Return"),
        ("ADJUSTMENT", "Stock Adjustment"),
    ]

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES
    )

    # Positive values add stock; negative values remove stock.
    quantity = models.IntegerField(
        validators=[MinValueValidator(-1000000)]
    )

    reason = models.TextField(blank=True)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant} - {self.quantity}"
