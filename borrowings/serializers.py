from datetime import datetime
from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer


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
            "book",
            "expected_return_date",

        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)

        borrow_date = datetime.today()
        attrs["borrow_date"] = borrow_date
        Borrowing.validate_borrowing(
            attrs["book"].inventory,
            serializers.ValidationError
        )
        return data

    def create(self, validated_data):
        book = validated_data["book"]
        expected_return_date = validated_data["expected_return_date"]

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            book=book,
            expected_return_date=expected_return_date
        )

        book.inventory -= 1
        book.save()

        return borrowing
