from rest_framework import serializers

from borrowings.serializers import BorrowingReadSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "pay_type",
            "borrowing",
            "money_to_pay",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingReadSerializer()

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "pay_type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
