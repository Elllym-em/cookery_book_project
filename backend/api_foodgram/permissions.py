from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение чтения данных для всех пользователей,
    для небезопасных методов - только администратор.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class IsAuthor(permissions.BasePermission):
    """ Разрешение на изменение и удаление данных только для автора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """ Разрешение на изменение и удаление данных только для автора."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )


class IsAuthForUsers(permissions.BasePermission):
    """
    Разрешение для неавторизованных пользователей
    только на получение списка юзеров.
    """

    def has_permission(self, request, view):
        return (
            request.method == 'list'
            or request.user.is_authenticated
        )
