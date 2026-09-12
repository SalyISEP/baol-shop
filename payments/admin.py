from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "method",
        "amount",
        "status",
        "transaction_reference",
        "created_at",
    )

    list_filter = (
        "method",
        "status",
        "created_at",
    )

    search_fields = (
        "order__customer_name",
        "order__phone",
        "transaction_reference",
    )

    readonly_fields = (
        "order",
        "amount",
        "created_at",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )