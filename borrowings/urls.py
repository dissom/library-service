from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import (
    BorrowingReturnAPIView,
    BorrowingViewSet
)


router = DefaultRouter()
router.register("", BorrowingViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/return/",
        BorrowingReturnAPIView.as_view(),
        name="borrowing-return"
    ),
]


app_name = "borrowings"
