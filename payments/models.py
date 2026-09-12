from django.db import models
from orders.models import Order


class Payment(models.Model):

    METHOD_CHOICES = [
        ('cash', 'Paiement à la livraison'),
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
        ('bank', 'Virement bancaire'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échec'),
        ('refunded', 'Remboursé'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    transaction_reference = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Paiement commande #{self.order.id}"