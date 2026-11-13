from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
