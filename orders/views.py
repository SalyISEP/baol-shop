from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product, ProductVariant
from deliveries.models import DeliveryZone, Delivery
from payments.models import Payment
from .models import Order, OrderItem


def checkout(request):

    cart = request.session.get("panier", {})

    if not cart:
        messages.error(request, "Votre panier est vide.")
        return redirect("panier")

    items = []
    subtotal = Decimal("0.00")

    # ==============================
    # VERIFICATION DU PANIER
    # ==============================

    for key, data in cart.items():

        product = get_object_or_404(
            Product,
            id=data["product_id"]
        )

        quantity = int(data.get("quantity", 0))

        if quantity <= 0:
            continue

        variant = None

        # Produit avec variante
        if data.get("variant_id"):

            variant = get_object_or_404(
                ProductVariant,
                id=data["variant_id"],
                product=product
            )

            if variant.stock < quantity:
                messages.error(
                    request,
                    f"Stock insuffisant pour {product.name}."
                )
                return redirect("panier")

        # Produit sans variante
        else:

            if product.stock < quantity:
                messages.error(
                    request,
                    f"Stock insuffisant pour {product.name}."
                )
                return redirect("panier")

        price = product.get_price()
        item_subtotal = price * quantity

        subtotal += item_subtotal

        items.append({
            "key": key,
            "product": product,
            "variant": variant,
            "quantity": quantity,
            "price": price,
            "subtotal": item_subtotal,
        })

    if not items:
        messages.error(request, "Votre panier est vide.")
        return redirect("panier")

    # ==============================
    # ZONES DE LIVRAISON
    # ==============================

    zones = DeliveryZone.objects.filter(
        active=True
    ).order_by("name")

    # ==============================
    # VALIDATION COMMANDE
    # ==============================

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        zone_id = request.POST.get("zone")

        payment_method = request.POST.get(
            "payment_method",
            ""
        ).strip()

        # ------------------------------
        # CHAMPS OBLIGATOIRES
        # ------------------------------

        if not customer_name:
            messages.error(
                request,
                "Veuillez saisir votre nom."
            )
            return redirect("checkout")

        if not phone:
            messages.error(
                request,
                "Veuillez saisir votre numéro de téléphone."
            )
            return redirect("checkout")

        if not address:
            messages.error(
                request,
                "Veuillez saisir votre adresse."
            )
            return redirect("checkout")

        if not zone_id:
            messages.error(
                request,
                "Veuillez choisir votre zone de livraison."
            )
            return redirect("checkout")

        if not payment_method:
            messages.error(
                request,
                "Veuillez choisir un mode de paiement."
            )
            return redirect("checkout")

        # ------------------------------
        # VERIFICATION PAIEMENT
        # ------------------------------

        allowed_payment_methods = {
            "cash",
            "wave",
            "orange_money",
            "bank",
        }

        if payment_method not in allowed_payment_methods:
            messages.error(
                request,
                "Mode de paiement invalide."
            )
            return redirect("checkout")

        # ------------------------------
        # ZONE
        # ------------------------------

        zone = get_object_or_404(
            DeliveryZone,
            id=zone_id,
            active=True
        )

        delivery_fee = zone.fee
        total = subtotal + delivery_fee

        # ==============================
        # CREATION TRANSACTIONNELLE
        # ==============================

        with transaction.atomic():

            order = Order.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                city=zone.name,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=total,
                status="pending",
            )

            # ==========================
            # ARTICLES + STOCK
            # ==========================

            for item in items:

                product = Product.objects.select_for_update().get(
                    id=item["product"].id
                )

                variant = None

                # --------------------------
                # VARIANTE
                # --------------------------

                if item["variant"]:

                    variant = ProductVariant.objects.select_for_update().get(
                        id=item["variant"].id,
                        product=product
                    )

                    if variant.stock < item["quantity"]:

                        messages.error(
                            request,
                            f"Stock insuffisant pour {product.name}."
                        )

                        transaction.set_rollback(True)

                        return redirect("panier")

                    variant.stock -= item["quantity"]
                    variant.save(
                        update_fields=["stock"]
                    )

                    variant_description = str(variant)

                # --------------------------
                # PRODUIT STANDARD
                # --------------------------

                else:

                    if product.stock < item["quantity"]:

                        messages.error(
                            request,
                            f"Stock insuffisant pour {product.name}."
                        )

                        transaction.set_rollback(True)

                        return redirect("panier")

                    product.stock -= item["quantity"]

                    product.save(
                        update_fields=[
                            "stock",
                            "updated_at"
                        ]
                    )

                    variant_description = ""

                # --------------------------
                # ORDER ITEM
                # --------------------------

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    product_name=product.name,
                    variant_description=variant_description,
                    quantity=item["quantity"],
                    unit_price=item["price"],
                    subtotal=item["subtotal"],
                )

            # ==========================
            # PAIEMENT
            # ==========================

            Payment.objects.create(
                order=order,
                method=payment_method,
                amount=total,
                status="pending",
            )

            # ==========================
            # LIVRAISON
            # ==========================

            Delivery.objects.create(
                order=order,
                zone=zone,
                address=address,
                city=zone.name,
                delivery_fee=delivery_fee,
                estimated_duration=zone.estimated_duration,
                status="pending",
            )

        # ==============================
        # VIDER LE PANIER
        # ==============================

        request.session["panier"] = {}
        request.session.modified = True

        return redirect(
            "commande_confirmation",
            order_id=order.id
        )

    # ==============================
    # AFFICHAGE CHECKOUT
    # ==============================

    return render(
        request,
        "orders/checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "zones": zones,
        }
    )


def commande_confirmation(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id
    )

    # Une commande liée à un compte
    # ne doit être visible que par son propriétaire.
    if order.user_id:

        if not request.user.is_authenticated:
            return redirect(
                f"/compte/connexion/?next=/commande/confirmation/{order.id}/"
            )

        if order.user_id != request.user.id:
            return redirect("mon_compte")

    return render(
        request,
        "orders/confirmation.html",
        {
            "order": order
        }
    )