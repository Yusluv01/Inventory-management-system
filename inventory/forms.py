
from django import forms
from products.models import ProductVariant


class StockAdjustmentForm(forms.Form):

    ACTION_CHOICES = [
        ("ADD", "Add stock"),
        ("REMOVE", "Remove stock"),
    ]

    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.filter(
            is_active=True
        ).select_related("product").order_by("product__name"),
        label="Product variant"
    )

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        label="Adjustment type"
    )

    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity"
    )

    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Explain why this stock adjustment is being made."
        }),
        label="Reason"
    )
