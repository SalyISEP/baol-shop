from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.mon_compte,
        name="mon_compte"
    ),

    path(
        "inscription/",
        views.inscription,
        name="inscription"
    ),

    path(
        "connexion/",
        views.connexion,
        name="connexion"
    ),

    path(
        "deconnexion/",
        views.deconnexion,
        name="deconnexion"
    ),

    path(
        "commande/<int:order_id>/",
        views.commande_detail,
        name="compte_commande_detail"
    ),
]