from django.contrib import admin
from .models import DeliveryZone, Delivery


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "fee",
        "estimated_duration",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "name",
    )

    list_editable = (
        "fee",
        "estimated_duration",
        "active",
    )

    ordering = (
        "name",
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "city",
        "delivery_fee",
        "estimated_duration",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "city",
        "created_at",
    )

    search_fields = (
        "order__customer_name",
        "order__phone",
        "city",
        "address",
    )

    readonly_fields = (
        "order",
        "zone",
        "address",
        "city",
        "delivery_fee",
        "estimated_duration",
        "created_at",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )