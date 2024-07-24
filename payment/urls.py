from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payment.views import (
    PaymentCancelView,
    PaymentSuccessView,
    PaymentViewSet,
    PaymentRenewalView
)


router = DefaultRouter()
router.register("", PaymentViewSet)


urlpatterns = [
    path("payments/", include(router.urls)),
    path(
        "payments-renew/",
        PaymentRenewalView.as_view(),
        name="payment-renewal"
    ),
    path(
        "success/",
        PaymentSuccessView.as_view(),
        name="payment-success"
    ),
    path(
        "cancel/",
        PaymentCancelView.as_view(),
        name="payment-cancel"
    ),
]


app_name = "payment"
