import functools

from .exceptions import NoPermissionException
from .shortcuts import get_user_permissions_map
from .utils import validate_permission


def required_permission(permission):
    permissions = validate_permission(permission)

    def decorate(func):
        @functools.wraps(func)
        def wrapper(view, request, *args, **kwargs):
            if hasattr(request, 'user'):
                user_permissions = get_user_permissions_map(request.user)
                for p in permissions:
                    if p in user_permissions:
                        return func(view, request, *args, **kwargs)
            raise NoPermissionException()
        return wrapper
    return decorate


def required_func_permission(permission):
    permissions = validate_permission(permission)

    def decorate(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if hasattr(request, 'user'):
                user_permissions = get_user_permissions_map(request.user)
                for p in permissions:
                    if p in user_permissions:
                        return func(request, *args, **kwargs)
            raise NoPermissionException()
        return wrapper
    return decorate
