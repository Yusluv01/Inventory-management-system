from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Q, F


class Purchase(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ORDERED", "Ordered"),
        ("PARTIAL", "Partially Received"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchases"
    )

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    expected_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_purchases"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference

    @property
    def total_cost(self):
        return sum(
            item.quantity_ordered * item.unit_cost
            for item in self.items.all()
        )


class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="purchase_items"
    )

    quantity_ordered = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    quantity_received = models.PositiveIntegerField(
        default=0
    )

    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=["purchase", "variant"],
                name="unique_variant_per_purchase"
            ),
            models.CheckConstraint(
                condition=Q(
                    quantity_received__lte=F("quantity_ordered")
                ),
                name="received_not_more_than_ordered"
            ),
        ]

    def __str__(self):
        return f"{self.variant} - {self.quantity_ordered} units"

    @property
    def outstanding_quantity(self):
        return self.quantity_ordered - self.quantity_received
