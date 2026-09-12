from django.contrib import admin

from .models import Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

    fields = (
        "color",
        "size",
        "pointure",
        "stock",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "price",
        "promo_price",
        "stock_total",
        "disponibilite",
        "created_at",
    )

    list_filter = (
        "category",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "price",
        "promo_price",
    )

    inlines = (
        ProductVariantInline,
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "category",
                    "name",
                    "description",
                    "image",
                )
            }
        ),
        (
            "Prix",
            {
                "fields": (
                    "price",
                    "promo_price",
                )
            }
        ),
        (
            "Stock",
            {
                "fields": (
                    "stock",
                )
            }
        ),
        (
            "Anciennes caractéristiques",
            {
                "classes": ("collapse",),
                "fields": (
                    "color",
                    "size",
                )
            }
        ),
        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )

    def stock_total(self, obj):
        return obj.total_stock()

    stock_total.short_description = "Stock total"

    def disponibilite(self, obj):

        stock = obj.total_stock()

        if stock <= 0:
            return "❌ Rupture"

        if stock <= 5:
            return f"⚠️ Faible ({stock})"

        return f"✅ Disponible ({stock})"

    disponibilite.short_description = "Disponibilité"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product",
        "color",
        "size",
        "pointure",
        "stock",
    )

    list_filter = (
        "color",
        "size",
        "pointure",
    )

    search_fields = (
        "product__name",
        "color",
        "size",
        "pointure",
    )

    list_editable = (
        "stock",
    )