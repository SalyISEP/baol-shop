from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product, ProductVariant


def ajouter_panier(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    variant_id = request.POST.get("variant_id")

    cart = request.session.get("panier", {})

    if product.variants.exists():

        if not variant_id:
            return redirect(
                "product_detail",
                product_id=product.id
            )

        variant = get_object_or_404(
            ProductVariant,
            id=variant_id,
            product=product
        )

        key = f"{product.id}_{variant.id}"

        current_quantity = cart.get(
            key,
            {}
        ).get("quantity", 0)

        if variant.stock <= 0:
            return redirect(
                "product_detail",
                product_id=product.id
            )

        if current_quantity + quantity > variant.stock:
            quantity = variant.stock - current_quantity

        if quantity <= 0:
            return redirect("panier")

        cart[key] = {
            "product_id": product.id,
            "variant_id": variant.id,
            "quantity": current_quantity + quantity,
        }

    else:

        key = str(product.id)

        current_quantity = cart.get(
            key,
            {}
        ).get("quantity", 0)

        if product.stock <= 0:
            return redirect(
                "product_detail",
                product_id=product.id
            )

        if current_quantity + quantity > product.stock:
            quantity = product.stock - current_quantity

        if quantity <= 0:
            return redirect("panier")

        cart[key] = {
            "product_id": product.id,
            "variant_id": None,
            "quantity": current_quantity + quantity,
        }

    request.session["panier"] = cart
    request.session.modified = True

    return redirect("panier")


def diminuer_panier(request, key):
    cart = request.session.get("panier", {})

    if key in cart:
        cart[key]["quantity"] -= 1

        if cart[key]["quantity"] <= 0:
            del cart[key]

    request.session["panier"] = cart
    request.session.modified = True

    return redirect("panier")


def augmenter_panier(request, key):
    cart = request.session.get("panier", {})

    if key not in cart:
        return redirect("panier")

    data = cart[key]

    product = get_object_or_404(
        Product,
        id=data["product_id"]
    )

    quantity = data["quantity"]

    if data.get("variant_id"):

        variant = get_object_or_404(
            ProductVariant,
            id=data["variant_id"],
            product=product
        )

        if quantity >= variant.stock:
            return redirect("panier")

    else:

        if quantity >= product.stock:
            return redirect("panier")

    data["quantity"] += 1

    cart[key] = data

    request.session["panier"] = cart
    request.session.modified = True

    return redirect("panier")


def supprimer_panier(request, key):
    cart = request.session.get("panier", {})

    if key in cart:
        del cart[key]

    request.session["panier"] = cart
    request.session.modified = True

    return redirect("panier")


def panier(request):
    cart = request.session.get("panier", {})

    items = []
    total = 0

    for key, data in list(cart.items()):

        product = get_object_or_404(
            Product,
            id=data["product_id"]
        )

        variant = None

        if data.get("variant_id"):

            variant = get_object_or_404(
                ProductVariant,
                id=data["variant_id"],
                product=product
            )

            stock = variant.stock

        else:
            stock = product.stock

        if data["quantity"] > stock:
            data["quantity"] = stock

        if data["quantity"] <= 0:
            del cart[key]
            continue

        price = product.get_price()
        quantity = data["quantity"]
        subtotal = price * quantity

        total += subtotal

        items.append({
            "key": key,
            "product": product,
            "variant": variant,
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal,
            "stock": stock,
        })

    request.session["panier"] = cart
    request.session.modified = True

    return render(
        request,
        "cart/panier.html",
        {
            "items": items,
            "total": total,
        }
    )
