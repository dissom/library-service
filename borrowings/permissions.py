from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only authenticated users to view their own borrowings
    and allow admins to view all borrowings.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return obj.user == request.user or request.user.is_staff

        return request.user.is_staff
