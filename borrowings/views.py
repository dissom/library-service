from rest_framework import viewsets, mixins

from borrowings.models import Borrowing
from borrowings.permissions import IsAuthenticatedAndOwnerOrAdmin
from borrowings.serializers import (
    BorrowingReadSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    permission_classes = (IsAuthenticatedAndOwnerOrAdmin,)

    def get_serializer_class(self):

        serializer = BorrowingReadSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
