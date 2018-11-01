from django.contrib.auth import get_user_model

from .exceptions import NoPermissionException, NoLoginException
from .shortcuts import get_user_permissions_map
from .utils import validate_permission


class AuthorizedPermission(object):

    def __init__(self, permission):
        self.permissions = validate_permission(permission)

    def has_permission(self, request, *args, **kwargs):
        if hasattr(request, 'user'):
            user_permissions = get_user_permissions_map(request.user)
            for p in self.permissions:
                if p in user_permissions:
                    return True
        raise NoPermissionException()


class OauthBackend(object):

    def authenticate(self, request, **kwargs):
        if not hasattr(request, 'user'):
            raise NoLoginException()
        user = request.user
        if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            raise NoLoginException()
        return True

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model._default_manager.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
