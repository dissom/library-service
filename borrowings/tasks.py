from borrowings.overdue_borrowings import check_overdue_borrowings

from celery import shared_task


@shared_task
def check_borrowings() -> None:
    check_overdue_borrowings()
