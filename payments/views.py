from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect

from .models import Payment


@staff_member_required
def confirmer_paiement(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    if request.method == "POST":

        reference = request.POST.get(
            "transaction_reference",
            ""
        ).strip()

        payment.transaction_reference = reference
        payment.status = "paid"
        payment.save(
            update_fields=[
                "transaction_reference",
                "status",
            ]
        )

        messages.success(
            request,
            f"Paiement de la commande #{payment.order.id} confirmé."
        )

    return redirect("/admin/payments/payment/")