from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer
from tests.test_books import sample_book


BORROWINGS_URL = reverse("borrowings:borrowing-list")


def sample_borrowing(**kwargs):
    user = kwargs.get("user", get_user_model().objects.first())
    book = Book.objects.create(
        title="Sample Book",
        author="Sample Author",
        cover=Book.CoverChoices.HARD.name,
        inventory=10,
        daily_fee=1.00,
    )
    borrow_date = kwargs.get("borrowing_date", datetime.today().date())
    expected_return_date = kwargs.get(
        "expected_return_date", borrow_date + timedelta(days=7)
    )
    defaults = {
        "user": user,
        "book": book,
        "borrow_date": borrow_date,
        "expected_return_date": expected_return_date,
    }
    defaults.update(kwargs)

    return Borrowing.objects.create(**defaults)


def detail_borrowing_url(borrowing_id: int):
    return reverse("borrowings:borrowing-detail", kwargs={"pk": borrowing_id})


class UnauthenticatedUserBorrowingsTestView(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpassword"
        )

    def test_unauth_borrowing_list(self):
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserBorrowingsTestView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpassword"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other_user@test.com", password="other_testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_auth_borrowing_list(self):

        sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingReadSerializer(borrowings, many=True)
        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.data["results"], serializer.data)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertNotEqual(response.data["results"], serializer.data)

    def test_auth_borrowing_create(self):

        date = datetime.today().date()
        book = sample_book()
        data = {
            "book": book.id,
            "borrowing_date": date,
            "expected_return_date": date + timedelta(days=7),
            "user": self.user,
        }

        response = self.client.post(BORROWINGS_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_other_borrowing_detail(self):

        borrowing = sample_borrowing(user=self.other_user)

        url = detail_borrowing_url(borrowing.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminUserBorrowingsTestView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="adminpassword",
            is_staff=True,
        )
        self.other_user = get_user_model().objects.create_user(
            email="other_user@test.com", password="other_testpassword"
        )
        self.client.force_authenticate(self.admin_user)

    def test_admin_borrowing_list(self):

        sample_borrowing(user=self.admin_user)
        sample_borrowing(user=self.other_user)

        borrowings = Borrowing.objects.all()

        serializer = BorrowingReadSerializer(borrowings, many=True)
        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_borrowing_detail(self):

        borrowing = sample_borrowing(user=self.other_user)

        url = detail_borrowing_url(borrowing.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
