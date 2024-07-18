from rest_framework import viewsets, mixins, generics, status
from rest_framework.response import Response


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
    mixins.CreateModelMixin,
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

    def get_serializer_class(self):
        if self.action == "create":
            serializer = BorrowingCreateSerializer
        elif self.action == "return_book":
            serializer = BorrowingReturnSerializer
        else:
            serializer = BorrowingReadSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BorrowingReturnAPIView(
    generics.CreateAPIView
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer

    def post(self, request, pk=None):

        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
