from django.contrib.auth import get_user

from .models import Permission
from .config import default_permission_prefix, super_user_filter


def __get_user_permission_filter(user):
    return dict(
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    )


def __get_permission_queryset():
    queryset = Permission.objects.filter(state=1)
    return queryset


def __get_user_permission_queryset(user):
    queryset = __get_permission_queryset()
    if not is_super_user(user):
        where = __get_user_permission_filter(user)
        queryset = queryset.filter(**where)
    return queryset


def __get_custom_permission_queryset(user=None):
    if user is not None:
        queryset = __get_user_permission_queryset(user)
    else:
        queryset = __get_permission_queryset()
    queryset = queryset.exclude(name__startswith=default_permission_prefix)
    return queryset


def __get_default_permission_queryset(user=None):
    if user is not None:
        queryset = __get_user_permission_queryset(user)
    else:
        queryset = __get_permission_queryset()
    queryset = queryset.filter(name__startswith=default_permission_prefix)
    return queryset


def get_user_obj(dj_request):
    return get_user(dj_request)


def is_super_user(user):
    result = False
    for k, v in super_user_filter.items():
        if not hasattr(user, k) or getattr(user, k) != v:
            break
    else:
        result = True
    return result


def has_manage_permission(dj_request):
    user = get_user_obj(dj_request)
    queryset = __get_default_permission_queryset(user=user)
    return queryset.exists()


def get_user_permissions_map(dj_request):
    user = get_user_obj(dj_request)
    queryset = __get_user_permission_queryset(user)
    query = queryset.values_list('name', 'state')
    return dict(query)


def get_user_default_permissions_name(dj_request):
    user = get_user_obj(dj_request)
    queryset = __get_default_permission_queryset(user=user)
    query = queryset.values_list('name', 'state')
    return dict(query).keys()


def get_user_custom_permissions_name(dj_request):
    user = get_user_obj(dj_request)
    queryset = __get_custom_permission_queryset(user=user)
    query = queryset.values_list('name', 'state')
    return dict(query).keys()
