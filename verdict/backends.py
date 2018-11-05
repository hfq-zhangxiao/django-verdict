from django.contrib.auth import get_user_model

from .exceptions import NoPermissionException, NoLoginException
from .shortcuts import get_user_permissions_map


class AuthorizedPermission(object):

    action_mapping = {
        'GET': 'read',
        'HEAD': 'read',
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
        'OPTIONS': 'read',
    }

    def has_permission(self, request, view):
        if not hasattr(request, 'user'):
            raise NoPermissionException()
        full_permission = '{permission}.{action}'.format(
            permission=getattr(view, 'permission', ''),
            action=self.action_mapping.get(request._request.method.upper()),
        )
        if full_permission in get_user_permissions_map(request.user):
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
