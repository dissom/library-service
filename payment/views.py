from django.shortcuts import redirect
import stripe
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from borrowings.helpers.payment import create_payment_session
from borrowings.helpers.telegram import send_message
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
)


def update_payment_status(payment, new_status, send_notification=False):
    payment.status = new_status
    payment.save()
    if send_notification:
        message = (
            f"Payment Successful:\n"
            f"Money to pay: ${payment.money_to_pay} USD\n"
            f"New Borrowing Created:\n"
            f"Book: {payment.borrowing.book.title} "
            f"({payment.borrowing.book.author})\n"
            f"User: {payment.borrowing.user.email}\n"
            f"Borrow Date: {payment.borrowing.borrow_date}\n"
            f"Expected Return Date: {
                payment.borrowing.expected_return_date
            }"
        )
        send_message(message)


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all().select_related()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(borrowing__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer
        return PaymentDetailSerializer

    def list(self, request, *args, **kwargs):
        """
        Retieve full list if is admin,
        else users see only their own payments.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific payment by ID.
        """
        return super().retrieve(request, *args, **kwargs)


class PaymentRenewalView(APIView):

    def post(self, request, *args, **kwargs):
        """ Renewal session ID & URL. """
        user = self.request.user

        payment = Payment.objects.filter(
            status="EXPIRED", borrowing__user=user
        ).first()
        if payment:
            new_session = create_payment_session(
                payment.borrowing,
                payment.money_to_pay,
                Payment.PaymentType.PAYMENT.name
            )
            update_payment_status(
                payment,
                new_session,
                send_notification=True
            )

            return Response(
                {
                    "detail": "Payment session renewed.",
                    "session_id": new_session.id,
                    "session_url": new_session.url
                }
            )
        return Response(
            {"detail": "No expired payment session found for renewal."},
            status=status.HTTP_404_NOT_FOUND
        )


class PaymentSuccessView(APIView):
    """
    Updates the status of a payment to 'PAID'
    based on the session ID provided in the query parameters.
    Sends a notification message about the new borrowing.
    """
    def get(self, request, *args, **kwargs) -> Response:
        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        payment = Payment.objects.get(session_id=session_id)

        if session.get("payment_status") == "paid":
            update_payment_status(
                payment,
                Payment.PaymentStatus.PAID.name,
                send_notification=True
            )

            return Response({"detail": "Payment succeeded!"})


class PaymentCancelView(APIView):
    """
    Informs the user that their payment session is still available
    for 24 hours and prompts them to complete the payment within that period.
    """
    def get(self, request, *args, **kwargs) -> Response:
        return Response(
            {
                "detail": "Your payment session is still "
                "available for 24 hours. Please complete your "
                "payment within this period."
            }
        )
