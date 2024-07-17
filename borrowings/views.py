from rest_framework import viewsets, mixins

from borrowings.models import Borrowing
from borrowings.permissions import IsAuthenticatedAndOwnerOrAdmin
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReadSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    permission_classes = (IsAuthenticatedAndOwnerOrAdmin,)
    serializer_class = BorrowingReadSerializer

    def get_queryset(self):
        """Retrieve borrowings with filters"""
        queryset = self.queryset
        user = self.request.user
        user_id = self.request.query_params.get("user_id")

        if user.is_staff and user_id:
            user_id = int(user_id)
            queryset = queryset.filter(user_id=user_id)

        elif not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")

        if is_active:
            is_active = True if is_active.lower() == "true" else False
            queryset = queryset.filter(is_active=is_active)

        return queryset


class BorrowingCreateViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):

    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BorrowingReturnViewSet(
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
