from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book


BOOKS_URL = reverse("books:book-list")


def sample_book(**kwargs) -> Book:
    defaults = {
        "title": "Sample book",
        "author": "Smpmle author",
        "cover": Book.CoverChoices.HARD,
        "inventory": "10",
        "daily_fee": Decimal(value="1.00")
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


def detail_book_url(book_id):
    return reverse("books:book-detail", kwargs={"pk": book_id})


class UnauthenticatedReadOnlyBooksTestVew(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauth_list_required(self) -> None:

        sample_book()
        book_2 = sample_book(
            title="Sample book_2",
            author="Sample author_2"
        )
        book_2.save()

        response = self.client.get(BOOKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_unath_detail_required(self) -> None:

        book = sample_book()
        book_detail_url = reverse(
            "books:book-detail",
            kwargs={"pk": book.id}
        )
        response = self.client.get(book_detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedBooksTestVew(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@test.com",
            password="testuser1234",
        )
        self.client.force_authenticate(self.user)

    def test_auth_detail_required(self) -> None:

        book = sample_book()
        book_detail_url = reverse(
            "books:book-detail",
            kwargs={"pk": book.id}
        )
        response = self.client.get(book_detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_auth_cannot_create_delete(self):

        book = sample_book()
        book_detail_url = reverse(
            "books:book-detail",
            kwargs={"pk": book.id}
        )
        new_book_data = {
            "title": "New Book Title",
            "author": "New Author",
            "cover": Book.CoverChoices.HARD,
            "inventory": 5,
            "daily_fee": Decimal("2.00"),
        }

        response = self.client.post(BOOKS_URL, data=new_book_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(book_detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


class AdminBooksTestVew(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@test.com",
            password="testuser1234",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self) -> None:

        book_data = {
            "title": "New Book Title",
            "author": "New Author",
            "cover": Book.CoverChoices.HARD,
            "inventory": 5,
            "daily_fee": Decimal("2.00"),
        }

        response = self.client.post(BOOKS_URL, book_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(pk=response.data["id"])
        for key in book_data:
            self.assertEqual(book_data[key], getattr(book, key))

    def test_auth_delete_book(self):

        book = sample_book()

        url = detail_book_url(book.id)

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
