from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from borrowings.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer
from tests.test_books import sample_book
from tests.test_borrowings import sample_borrowing


PAYMENTS_LIST = reverse("payment:payment-list")


def sample_payment(borrowing=None, **kwargs) -> Payment:

    defaults = {
        "session_url": "http://example.com",
        "session_id": "sess_123456789",
        "money_to_pay": 10.00,
        "pay_type": Payment.PaymentType.PAYMENT.name,
        "status": Payment.PaymentStatus.PAID.name,
        "borrowing": borrowing,
    }
    defaults.update(kwargs)
    return Payment.objects.create(**defaults)


def detail_payment_url(payment_id: int):
    return reverse("payment:payment-detail", kwargs={"pk": payment_id})


class AnauthenticatedUserPaymentTestView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword"
        )

    def test_unauth_payment_list(self):
        book = sample_book()
        borrowing: Borrowing = sample_borrowing(user=self.user, book=book)
        sample_payment(borrowing=borrowing)

        response = self.client.get(PAYMENTS_LIST)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPaymentTestView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other_user@test.com",
            password="other_testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_have_not_access_to_all_payments(self) -> None:
        book = sample_book()
        borrowing_1: Borrowing = sample_borrowing(
            user=self.user,
            book=book
        )
        borrowing_2: Borrowing = sample_borrowing(
            user=self.other_user,
            book=book
        )
        pay_1 = sample_payment(borrowing=borrowing_1)
        pay_2 = sample_payment(borrowing=borrowing_2)

        payments = Payment.objects.filter(borrowing__user=self.user)
        serializer = PaymentSerializer(payments, many=True)

        response = self.client.get(PAYMENTS_LIST)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        url_1 = detail_payment_url(pay_1.id)
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url_2 = detail_payment_url(pay_2.id)
        response = self.client.get(url_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
