from django.shortcuts import get_object_or_404, render

from categories.models import Category
from .models import Product


def home(request):
    products = Product.objects.all().order_by("-created_at")[:8]
    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "products/home.html",
        {
            "products": products,
            "categories": categories,
        }
    )


def boutique(request):
    products = Product.objects.all().order_by("-created_at")

    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "products/boutique.html",
        {
            "products": products,
            "categories": categories,
            "search": search,
            "selected_category": category_id,
        }
    )


def categorie(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    products = (
        Product.objects
        .filter(category=category)
        .order_by("-created_at")
    )

    return render(
        request,
        "products/categorie.html",
        {
            "category": category,
            "products": products,
        }
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants"),
        id=product_id
    )

    variants = product.variants.all()

    colors = sorted(
        set(v.color for v in variants if v.color)
    )

    sizes = sorted(
        set(v.size for v in variants if v.size)
    )

    pointures = sorted(
        set(v.pointure for v in variants if v.pointure)
    )

    return render(
        request,
        "products/detail.html",
        {
            "product": product,
            "variants": variants,
            "colors": colors,
            "sizes": sizes,
            "pointures": pointures,
        }
    )
