from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):

    class CoverChoices(models.TextChoices):
        HARD = "hard", "Hard"
        SOFT = "soft", "Soft"

    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    cover = models.CharField(
        max_length=50,
        choices=CoverChoices.choices
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    def __str__(self) -> str:
        return f"{self.title}: daily fee is ${self.daily_fee}"
