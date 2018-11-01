from django.contrib.auth import get_user_model

from .models import Permission
from .config import default_permission_prefix, super_user_filter, user_always_filter


def get_user_obj(lazy_user):
    pk = getattr(lazy_user, 'pk')
    return get_user_model().objects.filter(**user_always_filter).filter(pk=pk).first()


def is_super_user(user):
    return True
    result = True
    for k, v in super_user_filter.iteritems():
        if not hasattr(user, k) or getattr(user, k) != v:
            result = False
            break
    return result


def get_all_permissions():
    return Permission.objects.filter(state=1)


def get_custom_permissions():
    return Permission.objects.filter(state=1).exclude(name__startswith=default_permission_prefix)


def get_all_default_permissions_name():
    data = Permission.objects.filter(
        state=1,
        name__startswith=default_permission_prefix
    ).values_list('name', 'state')
    return dict(data).keys()


def get_all_permissions_map():
    obj = get_all_permissions()
    data = obj.values_list('name', 'state')
    return dict(data)


def get_all_permissions_name():
    maps = get_all_permissions_map()
    return maps.keys()


def get_custom_permissions_map():
    obj = get_custom_permissions()
    data = obj.values_list('name', 'state')
    return dict(data)


def get_custom_permissions_name():
    maps = get_custom_permissions_map()
    return maps.keys()


def get_user_default_permissions_name(user):
    user = get_user_obj(user)
    if is_super_user(user):
        return get_all_default_permissions_name()

    data = Permission.objects.filter(
        state=1,
        name__startswith=default_permission_prefix,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data).keys()


def get_user_permissions_map(user):
    if not isinstance(user, get_user_model()):
        user = get_user_obj(user)
    if is_super_user(user):
        return get_all_permissions_map()

    data = Permission.objects.filter(
        state=1,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data)


def get_user_custom_permissions_name(user):
    user = get_user_obj(user)
    if is_super_user(user):
        return get_custom_permissions_name()

    data = Permission.objects.exclude(name__startswith=default_permission_prefix).filter(
        state=1,
        grouppermission__state=1,
        grouppermission__group__state=1,
        grouppermission__group__groupuser__state=1,
        grouppermission__group__groupuser__user=user
    ).values_list('name', 'state')
    return dict(data).keys()
