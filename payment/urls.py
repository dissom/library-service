from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet


router = DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = router.urls

app_name = "payments"
