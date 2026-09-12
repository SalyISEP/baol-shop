from django.urls import path
from . import views


urlpatterns = [
    path(
        "confirmer/<int:payment_id>/",
        views.confirmer_paiement,
        name="confirmer_paiement"
    ),
]