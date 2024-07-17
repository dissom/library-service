from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import (
    BorrowingReturnAPIView,
    BorrowingViewSet
)


router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)


urlpatterns = [
    path("",include(router.urls)),
    path(
        "borrowings/<int:pk>/return/",
        BorrowingReturnAPIView.as_view(),
        name="borrowing-return"
    ),
]
print(router.urls)


app_name = "borrowings"
