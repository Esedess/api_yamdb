from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    """
    Права доступа: Администратор.
    read:admin
    write:admin
    """
    def has_permission(self, request, view):

        if request.user.is_anonymous:
            return False
        return (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == 'admin'
        )

    def has_object_permission(self, request, view, obj):

        if request.user.is_anonymous:
            return False
        return (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == 'admin'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа: anonim, модератор или администратор.
    read: anonim, moderator, admin
    write: moderator, admin
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.role == 'admin'
                    or request.user.is_superuser)))


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """
    Права доступа: Автор отзыва, модератор или администратор.
    read:user,moderator,admin
    write:user,moderator,admin
    """
    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.is_staff
            or request.user.is_superuser
        )
