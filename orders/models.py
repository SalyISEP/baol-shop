from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductVariant


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    customer_name = models.CharField(max_length=200)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=30)

    address = models.TextField()

    city = models.CharField(max_length=100)

    notes = models.TextField(blank=True)

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.customer_name}"

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # ==============================
        # SYNCHRONISATION LIVRAISON
        # ==============================

        try:
            delivery = self.delivery

            delivery_status = {
                'pending': 'pending',
                'confirmed': 'pending',
                'processing': 'preparing',
                'shipped': 'shipped',
                'delivered': 'delivered',
            }

            if self.status in delivery_status:

                delivery.status = delivery_status[self.status]

                delivery.save(
                    update_fields=['status']
                )

        except Exception:
            pass

        # ==============================
        # PAIEMENT À LA LIVRAISON
        # ==============================

        try:
            payment = self.payment

            if (
                self.status == 'delivered'
                and payment.method == 'cash'
            ):
                payment.status = 'paid'

                payment.save(
                    update_fields=['status']
                )

        except Exception:
            pass


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(
        max_length=200
    )

    variant_description = models.CharField(
        max_length=300,
        blank=True
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"