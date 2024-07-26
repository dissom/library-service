from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins, generics, status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from borrowings.models import Borrowing
from borrowings.permissions import IsAuthenticatedAndOwnerOrAdmin
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReadSerializer,
    BorrowingReturnSerializer
)
from payment.models import Payment


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
        else:
            serializer = BorrowingReadSerializer
        return serializer

    def create(self, request, *args, **kwargs) -> Response:
        """
        Create a new borrowing. Return the Stripe session
        Check if user has Pending or Expired payment.
        """
        user = self.request.user

        pending_payments = Payment.objects.filter(
            borrowing__user=user,
            status="PENDING" or "EXPIRED"
        )
        if pending_payments:
            raise ValidationError(
                "You have pending/expired payments. "
                "You cannot borrow new books until they are paid."
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save(user=user)

        payment = Payment.objects.get(borrowing=borrowing)

        return Response(
            {
                "detail": "Borrowing created successfully",
                "stripe_session_url": payment.session_url
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description=(
                    "Filter by user ID (admin only)"
                ),
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                description=(
                    "Filter by active status (true/false)"
                ),
                type=OpenApiTypes.STR,
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List borowings with filtering by 'user_id' for admins
        and 'is_active' only for logging user
        """
        return super().list(request, *args, **kwargs)


class BorrowingReturnAPIView(
    generics.CreateAPIView
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer

    def post(self, request, pk=None) -> Response:
        """
        Mark a borrowing as returned
        and handle overdue payments.
        """

        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        fine = serializer.save()

        payment = Payment.objects.get(borrowing=fine)

        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                "detail": "You ned to pay overdue",
                "stripe_session_url": payment.session_url
            },
            status=status.HTTP_200_OK,
            headers=headers
        )
