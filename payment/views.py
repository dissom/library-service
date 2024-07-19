from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.all().select_related()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        queryset = Payment.objects.all().select_related()
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer
        return PaymentDetailSerializer
