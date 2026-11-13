
from django.db import transaction
from django.core.exceptions import ValidationError

from products.models import ProductVariant
from .models import StockLevel, StockMovement


@transaction.atomic
def adjust_stock(variant_id, quantity, movement_type, reason="", user=None):
    """
    Add or remove stock while recording the movement.

    Positive quantity = stock entering the store.
    Negative quantity = stock leaving the store.
    """

    if quantity == 0:
        raise ValidationError("Quantity cannot be zero.")

    valid_types = dict(StockMovement.MOVEMENT_TYPES)

    if movement_type not in valid_types:
        raise ValidationError("Invalid stock movement type.")

    if movement_type in ["OPENING", "PURCHASE", "RETURN"] and quantity < 0:
        raise ValidationError(
            "This movement type must increase stock."
        )

    if movement_type == "SALE" and quantity > 0:
        raise ValidationError(
            "A sale must decrease stock."
        )

    if movement_type == "OPENING" and quantity < 0:
        raise ValidationError(
            "Opening stock must be positive."
        )

    if movement_type == "ADJUSTMENT" and not reason.strip():
        raise ValidationError(
            "Please provide a reason for the adjustment."
        )

    # Lock the variant to prevent simultaneous stock updates
    # from conflicting with each other.
    variant = ProductVariant.objects.select_for_update().get(
        pk=variant_id
    )

    stock, created = StockLevel.objects.get_or_create(
        variant=variant
    )

    new_quantity = stock.quantity_on_hand + quantity

    if new_quantity < 0:
        raise ValidationError(
            "Insufficient stock. Stock cannot go below zero."
        )

    stock.quantity_on_hand = new_quantity
    stock.save(update_fields=["quantity_on_hand", "updated_at"])

    movement = StockMovement.objects.create(
        variant=variant,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        performed_by=user
    )

    return movement
