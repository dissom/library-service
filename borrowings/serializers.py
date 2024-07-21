import stripe
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from rest_framework import serializers
from django.db.transaction import atomic

from payment.models import Payment
from borrowings.models import Borrowing
from books.serializers import BookSerializer
from borrowings.helpers.payment import create_payment_session


stripe.api_key = settings.STRIPE_SECRET_KEY


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.CharField(
        read_only=True,
        source="user.email"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
            "user",
        )
        read_only_fields = ("is_active", "actual_return_date")


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)

        Borrowing.validate_borrowing(
            attrs["book"].inventory,
            serializers.ValidationError
        )
        return data

    @atomic
    def create(self, validated_data):
        book = validated_data["book"]
        expected_return_date = validated_data["expected_return_date"]

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            book=book,
            expected_return_date=expected_return_date,
        )

        book.inventory -= 1
        book.save()

        total_fee = borrowing.calculate_total_fee()
        create_payment_session(
            borrowing,
            total_fee,
            Payment.PaymentType.PAYMENT
        )
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id",)

    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs)
        borrowing = self.instance
        if borrowing.actual_return_date:
            raise serializers.ValidationError(
                {
                    f"Borrowing with id: {borrowing.id}":
                        "This borrowing has already been returned."
                }
            )
        return data

    @atomic
    def update(self, instance, validated_data):
        instance.actual_return_date = datetime.today().date()
        overdue_fee = instance.calculate_overdue_fee()

        if overdue_fee > Decimal(0):
            create_payment_session(
                instance,
                overdue_fee,
                Payment.PaymentType.FINE
            )

        instance.return_book()
        instance.save()
        return instance
