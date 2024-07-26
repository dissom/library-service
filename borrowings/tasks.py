from datetime import datetime, timedelta

from django.conf import settings
import stripe
from borrowings.overdue_borrowings import check_overdue_borrowings

from celery import shared_task

from payment.models import Payment


@shared_task
def check_borrowings() -> None:
    check_overdue_borrowings()


@shared_task
def check_expired_payments():
    stripe.api_key = settings.STRIPE_SECRET_KEY

    pending_payments = Payment.objects.filter(status="PENDING")

    for payment in pending_payments:
        session = stripe.checkout.Session.retrieve(payment.session_id)

        if session["status"] == "expired":
            payment.status = Payment.PaymentStatus.EXPIRED
            payment.save()
