from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order


def inscription(request):
    if request.user.is_authenticated:
        return redirect("mon_compte")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect("inscription")

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("inscription")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect("inscription")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email est déjà utilisée.")
            return redirect("inscription")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            "Votre compte a été créé avec succès."
        )

        return redirect("mon_compte")

    return render(request, "comptes/inscription.html")


def connexion(request):
    if request.user.is_authenticated:
        return redirect("mon_compte")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("mon_compte")

        messages.error(
            request,
            "Nom d'utilisateur ou mot de passe incorrect."
        )

    return render(request, "comptes/connexion.html")


def deconnexion(request):
    logout(request)
    return redirect("home")


@login_required
def mon_compte(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .select_related()
        .order_by("-created_at")
    )

    return render(
        request,
        "comptes/mon_compte.html",
        {
            "orders": orders,
        }
    )


@login_required
def commande_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "comptes/commande_detail.html",
        {
            "order": order,
        }
    )