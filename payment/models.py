from django.conf import settings
from django.db import models
from enum import Enum

from borrowings.models import Borrowing


class Payment(models.Model):

    class PaymentStatus(Enum):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class PaymentType(Enum):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=20,
        choices=[(status.value[0], status.name) for status in PaymentStatus],
        default=PaymentStatus.PENDING.value[0]
    )
    type = models.CharField(
        max_length=20,
        choices=[(type.value[0], type.name) for type in PaymentType],
        default=PaymentType.PAYMENT.value[0]
    )
    borrowing = models.OneToOneField(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"Payment for Borrowing ID {self.borrowing_id}, "
            f"Type: {self.type}, Status: {self.status}"
        )
