from django.db import models
from orders.models import Order


class DeliveryZone(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    estimated_duration = models.CharField(
        max_length=100,
        default='1 à 3 jours'
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.name} - {self.fee} FCFA"


class Delivery(models.Model):

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('preparing', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery'
    )

    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    estimated_duration = models.CharField(
        max_length=100,
        default='1 à 3 jours'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Livraison commande #{self.order.id}"