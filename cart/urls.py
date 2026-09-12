from django.urls import path
from . import views

urlpatterns = [
    path("", views.panier, name="panier"),

    path(
        "ajouter/<int:product_id>/",
        views.ajouter_panier,
        name="ajouter_panier"
    ),

    path(
        "diminuer/<str:key>/",
        views.diminuer_panier,
        name="diminuer_panier"
    ),

    path(
        "supprimer/<str:key>/",
        views.supprimer_panier,
        name="supprimer_panier"
    ),

    path(
    "augmenter/<str:key>/",
    views.augmenter_panier,
    name="augmenter_panier"
    ),
]