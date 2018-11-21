from django.contrib.auth import get_user

from .models import Permission
from .config import default_permission_prefix, super_user_filter


def get_user_obj(dj_request):
    return get_user(dj_request)


def is_super_user(user):
    result = True
    for k, v in super_user_filter.items():
        if not hasattr(user, k) or getattr(user, k) != v:
            result = False
            break
    return result


def has_manage_permission(dj_request):
    user = get_user_obj(dj_request)
    if is_super_user(user):
        return True
    return Permission.objects.filter(
        state=1,
        name__startswith=default_permission_prefix,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).exists()


def _get_all_default_permissions_name():
    permission = Permission.objects.filter(
        state=1,
        name__startswith=default_permission_prefix
    ).values_list('name', 'state')
    return dict(permission).keys()


def _get_all_permissions_map():
    permission = Permission.objects.filter(state=1).values_list('name', 'state')
    return dict(permission)


def _get_custom_permissions_name():
    permission = Permission.objects.filter(state=1).exclude(
        name__startswith=default_permission_prefix).values_list('name', 'state')
    return dict(permission).keys()


def get_user_default_permissions_name(dj_request):
    user = get_user_obj(dj_request)
    if is_super_user(user):
        return _get_all_default_permissions_name()

    data = Permission.objects.filter(
        state=1,
        name__startswith=default_permission_prefix,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data).keys()


def get_user_permissions_map(dj_request):
    user = get_user_obj(dj_request)
    if is_super_user(user):
        return _get_all_permissions_map()

    data = Permission.objects.filter(
        state=1,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data)


def get_user_permissions_name(dj_request):
    return get_user_permissions_map(dj_request).keys()


def get_user_custom_permissions_name(dj_request):
    user = get_user_obj(dj_request)
    if is_super_user(user):
        return _get_custom_permissions_name()

    data = Permission.objects.exclude(name__startswith=default_permission_prefix).filter(
        state=1,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data).keys()
