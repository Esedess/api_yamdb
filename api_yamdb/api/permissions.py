from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Права доступа: Администратор.
    read: admin
    write: admin

    Superuser is always an admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа: Администратор или только чтение.
    read:authenticated, admin
    write:admin

    Superuser is always an admin.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    """
    Права доступа: Администратор, Модератор, Автор или только чтение.
    read: authenticated, author, moderator, admin
    write: author, moderator, admin

    Superuser is always an admin and a moderator.
    The admin is always a moderator.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_moderator
                or obj.author == request.user)
