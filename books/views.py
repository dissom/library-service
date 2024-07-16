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
