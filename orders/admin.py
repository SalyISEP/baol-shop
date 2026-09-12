from django.contrib import admin

from .models import Order, OrderItem
from payments.models import Payment
from deliveries.models import Delivery


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    fields = (
        "product_name",
        "variant_description",
        "quantity",
        "unit_price",
        "subtotal",
    )

    readonly_fields = (
        "product_name",
        "variant_description",
        "quantity",
        "unit_price",
        "subtotal",
    )


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    max_num = 1

    fields = (
        "method",
        "amount",
        "status",
        "transaction_reference",
        "created_at",
    )

    readonly_fields = (
        "amount",
        "created_at",
    )


class DeliveryInline(admin.StackedInline):
    model = Delivery
    extra = 0
    max_num = 1

    fields = (
        "zone",
        "address",
        "city",
        "delivery_fee",
        "status",
        "estimated_duration",
        "created_at",
    )

    readonly_fields = (
        "delivery_fee",
        "created_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "phone",
        "city",
        "formatted_total",
        "status",
        "payment_status",
        "delivery_status",
        "created_at",
    )

    list_filter = (
        "status",
        "city",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "phone",
        "email",
    )

    readonly_fields = (
        "user",
        "subtotal",
        "delivery_fee",
        "total",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "status",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline,
        PaymentInline,
        DeliveryInline,
    ]

    fieldsets = (
        (
            "👤 Informations client",
            {
                "fields": (
                    "user",
                    "customer_name",
                    "email",
                    "phone",
                )
            },
        ),

        (
            "📍 Adresse de livraison",
            {
                "fields": (
                    "address",
                    "city",
                    "notes",
                )
            },
        ),

        (
            "💰 Montants de la commande",
            {
                "fields": (
                    "subtotal",
                    "delivery_fee",
                    "total",
                )
            },
        ),

        (
            "📦 Statut de la commande",
            {
                "fields": (
                    "status",
                )
            },
        ),

        (
            "🕐 Historique",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Total", ordering="total")
    def formatted_total(self, obj):
        return f"{obj.total:,.0f} FCFA".replace(",", " ")


    @admin.display(description="Paiement")
    def payment_status(self, obj):

        try:
            payment = obj.payment

            labels = {
                "pending": "🟡 En attente",
                "paid": "🟢 Payé",
                "failed": "🔴 Échec",
                "refunded": "↩️ Remboursé",
            }

            return labels.get(
                payment.status,
                payment.get_status_display()
            )

        except Payment.DoesNotExist:
            return "—"

    @admin.display(description="Livraison")
    def delivery_status(self, obj):

        try:
            delivery = obj.delivery

            labels = {
                "pending": "🟡 En attente",
                "preparing": "🟠 En préparation",
                "shipped": "🚚 Expédiée",
                "delivered": "🟢 Livrée",
            }

            return labels.get(
                delivery.status,
                delivery.get_status_display()
            )

        except Delivery.DoesNotExist:
            return "—"