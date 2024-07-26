from rest_framework import viewsets
from books.models import Book
from books.serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [
                IsAdminUser,
            ]
        elif self.action == "retrieve":
            permission_classes = [
                IsAuthenticated,
            ]
        else:
            permission_classes = [
                AllowAny,
            ]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """ A list of books for all users."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve a specific book by ID for authenticated users. """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """ Create a new book only for admin users. """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """ Update existing book only with admin permissions. """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """ Partially update existing book only with admin permissions. """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """ Destroy existing book only with admin permissions. """
        return super().destroy(request, *args, **kwargs)
