from datetime import date, datetime
from decimal import Decimal
from django.db import models

from books.models import Book
from borrowings.validators import validate_expected_return_date
from library_service import settings


FINE_MULTIPLIER = 2


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(
        validators=[validate_expected_return_date]
    )
    actual_return_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowing"
    )

    def __str__(self) -> str:
        return (
            f"Borrowing {self.id}: {self.book.title} "
            f"by User: {self.user.email}"
        )

    @staticmethod
    def validate_borrowing(
        inventory,
        error_to_raise
    ) -> None:
        if inventory == 0:
            raise error_to_raise(
                {"book": "Book inventory is zero. Cannot borrow this book."}
            )

    def clean(self) -> None:
        Borrowing.validate_borrowing(
            self.book.inventory,
            ValueError
        )

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def return_book(self) -> None:
        self.actual_return_date = date.today()
        self.book.inventory += 1
        self.book.save()
        self.is_active = False
        self.save()

    def calculate_total_fee(self) -> Decimal:
        end_date = self.expected_return_date
        total_days = (end_date - self.borrow_date).days
        total_fee = Decimal(total_days) * self.book.daily_fee

        return total_fee

    def calculate_overdue_fee(self) -> Decimal:
        if not self.actual_return_date:
            self.actual_return_date = datetime.today().date()

        if self.actual_return_date <= self.expected_return_date:
            return Decimal(0)

        overdue_days = (
            self.actual_return_date - self.expected_return_date
        ).days
        daily_fee = self.book.daily_fee
        fine_multiplier = Decimal(FINE_MULTIPLIER)
        overdue_fee = overdue_days * daily_fee * fine_multiplier
        return overdue_fee
