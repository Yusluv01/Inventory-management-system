
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Purchase, PurchaseItem
from inventory.services import adjust_stock


@transaction.atomic
def place_purchase_order(purchase_id):
    """
    Change a draft purchase into an ordered purchase.
    """

    purchase = Purchase.objects.select_for_update().get(
        pk=purchase_id
    )

    if purchase.status != "DRAFT":
        raise ValidationError(
            "Only draft purchases can be placed as orders."
        )

    if not purchase.items.exists():
        raise ValidationError(
            "A purchase must contain at least one item."
        )

    if not purchase.supplier.is_active:
        raise ValidationError(
            "This supplier is inactive."
        )

    purchase.status = "ORDERED"
    purchase.save(update_fields=["status", "updated_at"])

    return purchase


@transaction.atomic
def receive_purchase_items(purchase_id, received_quantities, user=None):
    """
    Receive all or part of a purchase.

    received_quantities format:
    {
        purchase_item_id: quantity_received_now
    }
    """

    purchase = Purchase.objects.select_for_update().get(
        pk=purchase_id
    )

    if purchase.status not in ["ORDERED", "PARTIAL"]:
        raise ValidationError(
            "Only ordered or partially received purchases can be received."
        )

    items = list(
        PurchaseItem.objects.select_for_update().filter(
            purchase=purchase
        ).select_related("variant", "variant__product")
    )

    items_by_id = {item.id: item for item in items}

    if not received_quantities:
        raise ValidationError(
            "Enter at least one quantity to receive."
        )

    # Validate all submitted quantities before changing stock.
    validated_receipts = []

    for item_id, quantity in received_quantities.items():

        if item_id not in items_by_id:
            raise ValidationError(
                "An item does not belong to this purchase."
            )

        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise ValidationError(
                "Received quantities must be whole numbers."
            )

        if quantity <= 0:
            raise ValidationError(
                "Received quantities must be greater than zero."
            )

        item = items_by_id[item_id]

        if quantity > item.outstanding_quantity:
            raise ValidationError(
                f"Cannot receive more than the outstanding quantity "
                f"for {item.variant}."
            )

        validated_receipts.append((item, quantity))

    # Apply each receipt and update its purchase item.
    for item, quantity in validated_receipts:

        adjust_stock(
            variant_id=item.variant_id,
            quantity=quantity,
            movement_type="PURCHASE",
            reason=f"Goods received against purchase {purchase.reference}",
            user=user
        )

        item.quantity_received += quantity

        item.save(update_fields=["quantity_received"])

    # Update the overall purchase status.
    all_received = all(
        item.quantity_received == item.quantity_ordered
        for item in items
    )

    purchase.status = "RECEIVED" if all_received else "PARTIAL"

    purchase.save(update_fields=["status", "updated_at"])

    return purchase
