from django.contrib import admin
admin.site.index_template = "admin/index.html"
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from products.views import boutique, categorie, home
from products import views as products_views


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        home,
        name="home"
    ),

    path(
        "boutique/",
        boutique,
        name="boutique"
    ),

    path(
        "categorie/<int:category_id>/",
        categorie,
        name="categorie"
    ),

    path(
        "produit/<int:product_id>/",
        products_views.product_detail,
        name="product_detail"
    ),

    path(
        "panier/",
        include("cart.urls")
    ),

    path(
        "commande/",
        include("orders.urls")
    ),

    path(
        "compte/",
        include("comptes.urls")
    ),
    path(
    "paiement/",
    include("payments.urls")
),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )