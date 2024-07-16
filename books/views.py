from rest_framework import viewsets
from books.models import Book
from books.serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

