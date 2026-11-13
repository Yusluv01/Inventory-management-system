
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import F

from .models import StockLevel
from .forms import StockAdjustmentForm
from .services import adjust_stock


@login_required
@user_passes_test(lambda user: user.is_staff, login_url="/admin/login/")
def stock_list(request):

    form = StockAdjustmentForm()

    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)

        if form.is_valid():
            variant = form.cleaned_data["variant"]
            action = form.cleaned_data["action"]
            quantity = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]

            if action == "REMOVE":
                quantity = -quantity

            try:
                adjust_stock(
                    variant_id=variant.id,
                    quantity=quantity,
                    movement_type="ADJUSTMENT",
                    reason=reason,
                    user=request.user
                )

                messages.success(
                    request,
                    "Stock adjustment completed successfully."
                )

                return redirect("inventory:stock_list")

            except ValidationError as error:
                messages.error(request, " ".join(error.messages))

    stock_items = StockLevel.objects.select_related(
        "variant",
        "variant__product",
        "variant__product__category"
    )

    low_stock_items = stock_items.filter(
        quantity_on_hand__lte=F("reorder_level")
    )

    context = {
        "form": form,
        "stock_items": stock_items,
        "low_stock_items": low_stock_items,
        "total_variants": stock_items.count(),
        "low_stock_count": low_stock_items.count(),
    }

    return render(
        request,
        "inventory/stock_list.html",
        context
    )
