from django.contrib.auth import get_user_model

from .exceptions import NoPermissionException, NoLoginException
from .shortcuts import get_user_permissions_map
from .config import action_enum


class AuthorizedPermission(object):

    @staticmethod
    def __get_real_permission(request, permission):
        dj_request = getattr(request, '_request')
        method = getattr(dj_request, 'method', '')
        action = action_enum.get(method.upper())

        return '{permission}.{action}'.format(
            permission=permission, action=action
        )

    def has_permission(self, request, view):
        if not hasattr(view, 'permission'):
            raise NoPermissionException()
        if not view.permission:
            return True
        real_permission = self.__get_real_permission(request, view.permission)
        if real_permission in get_user_permissions_map(request):
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
