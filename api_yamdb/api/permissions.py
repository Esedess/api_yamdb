from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """
    Права доступа: только чтение.
    read: any
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    """
    Права доступа: Администратор.
    read: admin
    write: admin

    Superuser is always an admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(permissions.BasePermission):
    """
    Права доступа: Модератор.
    read: moderator
    write: moderator
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_moderator


class IsAuthenticatedOrOwner(permissions.IsAuthenticated):
    """
    Права доступа: Администратор, Модератор, Автор или только чтение.
    read, POST: authenticated
    UPDATE, DELETE: author
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
