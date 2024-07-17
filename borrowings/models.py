from django.db import models

from books.models import Book
from borrowings.validators import validate_expected_return_date
from library_service import settings


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
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Borrowing: {self.book.title} by User: {self.user.email}"
