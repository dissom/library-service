from django.core.exceptions import ValidationError
from datetime import date


def validate_expected_return_date(value):
    if value <= date.today().today():
        raise ValidationError(
            "Expected return date must be in the future."
        )
