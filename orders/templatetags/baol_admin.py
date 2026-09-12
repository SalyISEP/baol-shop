from django import template
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderItem
from products.models import Product
from payments.models import Payment
from deliveries.models import Delivery

register = template.Library()


@register.simple_tag
def baol_stats():

    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = now - timedelta(days=7)
    month = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    orders = Order.objects.all()
    products = Product.objects.all()

    realized_statuses = [
        "confirmed",
        "processing",
        "shipped",
        "delivered",
    ]

    # =========================
    # CHIFFRE D'AFFAIRES
    # =========================

    revenue = orders.filter(
        status__in=realized_statuses
    ).aggregate(total=Sum("total"))["total"] or 0

    pending_revenue = orders.filter(
        status="pending"
    ).aggregate(total=Sum("total"))["total"] or 0

    revenue_today = orders.filter(
        created_at__gte=today,
        status__in=realized_statuses
    ).aggregate(total=Sum("total"))["total"] or 0

    revenue_week = orders.filter(
        created_at__gte=week,
        status__in=realized_statuses
    ).aggregate(total=Sum("total"))["total"] or 0

    revenue_month = orders.filter(
        created_at__gte=month,
        status__in=realized_statuses
    ).aggregate(total=Sum("total"))["total"] or 0

    # =========================
    # STOCK
    # =========================

    available_products = sum(
        1 for product in products
        if product.is_available()
    )

    out_of_stock = sum(
        1 for product in products
        if not product.is_available()
    )

    low_stock = [
        product for product in products
        if 0 < product.total_stock() <= 5
    ]

    # =========================
    # MEILLEURS PRODUITS
    # =========================

    best_sellers = (
        OrderItem.objects
        .filter(order__status__in=realized_statuses)
        .values("product_name")
        .annotate(
            quantity_sold=Sum("quantity"),
            revenue=Sum("subtotal")
        )
        .order_by("-quantity_sold")[:5]
    )

    # =========================
    # GRAPHIQUE 7 JOURS
    # =========================

    sales_chart = []

    for i in range(6, -1, -1):

        date = (today - timedelta(days=i)).date()

        next_date = date + timedelta(days=1)

        amount = orders.filter(
            created_at__date=date,
            status__in=realized_statuses
        ).aggregate(
            total=Sum("total")
        )["total"] or 0

        sales_chart.append({
            "label": date.strftime("%d/%m"),
            "amount": amount,
        })

    max_sales = max(
        [item["amount"] for item in sales_chart],
        default=0
    )

    for item in sales_chart:
        if max_sales:
            item["height"] = int(
                (float(item["amount"]) / float(max_sales)) * 100
            )
        else:
            item["height"] = 5

    # =========================
    # PAIEMENTS
    # =========================

    pending_payments = Payment.objects.filter(
        status="pending"
    ).count()

    pending_payment_amount = Payment.objects.filter(
        status="pending"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # =========================
    # LIVRAISONS
    # =========================

    pending_deliveries = Delivery.objects.filter(
        status__in=["pending", "preparing", "shipped"]
    ).count()

    return {
        "orders_total": orders.count(),

        "pending": orders.filter(status="pending").count(),
        "confirmed": orders.filter(status="confirmed").count(),
        "processing": orders.filter(status="processing").count(),
        "shipped": orders.filter(status="shipped").count(),
        "delivered": orders.filter(status="delivered").count(),
        "cancelled": orders.filter(status="cancelled").count(),

        "revenue": revenue,
        "pending_revenue": pending_revenue,
        "revenue_today": revenue_today,
        "revenue_week": revenue_week,
        "revenue_month": revenue_month,

        "products": products.count(),
        "available_products": available_products,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,

        "customers": User.objects.filter(
            is_staff=False
        ).count(),

        "best_sellers": best_sellers,

        "sales_chart": sales_chart,

        "pending_payments": pending_payments,
        "pending_payment_amount": pending_payment_amount,

        "pending_deliveries": pending_deliveries,
    }


@register.simple_tag
def recent_orders():
    return Order.objects.all().order_by("-created_at")[:10]