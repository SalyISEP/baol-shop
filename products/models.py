from django.db import models


class Product(models.Model):

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    promo_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Stock général du produit.
    # Il sera progressivement remplacé par le stock des variantes.
    stock = models.PositiveIntegerField(default=0)

    # Anciens champs conservés pour compatibilité.
    color = models.CharField(
        max_length=100,
        blank=True
    )

    size = models.CharField(
        max_length=100,
        blank=True
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def get_price(self):
        """Retourne automatiquement le prix promotionnel s'il existe."""
        return self.promo_price if self.promo_price else self.price

    def total_stock(self):
        """Stock total de toutes les variantes."""
        variants_stock = sum(
            variant.stock
            for variant in self.variants.all()
        )

        if self.variants.exists():
            return variants_stock

        return self.stock

    def is_available(self):
        return self.total_stock() > 0

    def __str__(self):
        return self.name


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    color = models.CharField(
        max_length=100,
        blank=True
    )

    size = models.CharField(
        max_length=50,
        blank=True
    )

    pointure = models.CharField(
        max_length=20,
        blank=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):

        details = []

        if self.color:
            details.append(self.color)

        if self.size:
            details.append(f"Taille {self.size}")

        if self.pointure:
            details.append(f"Pointure {self.pointure}")

        if details:
            return f"{self.product.name} - {' / '.join(details)}"

        return f"{self.product.name} - Standard"