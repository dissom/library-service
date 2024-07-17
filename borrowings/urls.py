from rest_framework.routers import DefaultRouter

from borrowings.views import (
    BorrowingCreateViewSet,
    BorrowingReturnViewSet,
    BorrowingViewSet
)


router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register(
    "create-borrowing",
    BorrowingCreateViewSet,
    basename="create-borrowing"
),
router.register(
    "return-borrowing",
    BorrowingReturnViewSet,
    basename="return-borrowing"
)


urlpatterns = router.urls
print(router.urls)


app_name = "borrowings"
