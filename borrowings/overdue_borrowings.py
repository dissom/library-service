from datetime import datetime

from borrowings.helpers.telegram import send_message
from borrowings.models import Borrowing


def check_overdue_borrowings():
    today = datetime.today()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            send_telegram_notification(borrowing)
        return f"{len(overdue_borrowings)} overdue borrowings notified."

    return "No borrowings overdue today"


def send_telegram_notification(borrowing):
    message = (
        f"Overdue Borrowing:\n"
        f"Book: {borrowing.book.title}\n"
        f"User: {borrowing.user.email}\n"
        f"Expected Return Date: {borrowing.expected_return_date}\n"
        f"Borrow Date: {borrowing.borrow_date}"
    )
    send_message(message)
