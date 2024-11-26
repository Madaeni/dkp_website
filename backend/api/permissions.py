from rest_framework import permissions


class DkpPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        ):
            return True


class CharacterPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS
            or obj.user == request.user
            or request.user.is_staff
        ):
            return True
