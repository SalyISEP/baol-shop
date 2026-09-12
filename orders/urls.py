from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.checkout,
        name="checkout"
    ),

    path(
        "confirmation/<int:order_id>/",
        views.commande_confirmation,
        name="commande_confirmation"
    ),
]