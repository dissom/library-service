from rest_framework.routers import DefaultRouter

from borrowings.views import BorrowingCreateViewSet, BorrowingViewSet


router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register(
    "create-borrowing",
    BorrowingCreateViewSet,
    basename="create-borrowing"
)


urlpatterns = router.urls


app_name = "borrowings"
