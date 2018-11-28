import datetime
import math

from .config import PAGE_LIMIT
from .shortcuts import get_user_default_permissions_name


def models_to_dict(obj, fields=None, exclude=None):
    if exclude is None:
        exclude = list()
    if fields is not None and not isinstance(fields, (list, tuple)):
        raise Exception("fields: '{type}' object is not iterable".format(type=type(fields)))
    if exclude is not None and not isinstance(exclude, (list, tuple)):
        raise Exception("exclude: '{type}' object is not iterable".format(type=type(exclude)))

    data = dict()
    for field in obj._meta.concrete_fields:
        if (exclude is not None and field.name in exclude) or \
                (fields is not None and field.name not in fields):
            continue
        value = field.value_from_object(obj)
        if isinstance(value, datetime.datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, datetime.date):
            value = value.strftime('%Y-%m-%d')
        elif isinstance(value, unicode):
            value = value.encode('utf-8')
        data[field.name] = value
    return data


def validate_permission(permission):
    if not permission:
        raise Exception('permission can not be empty')
    if isinstance(permission, str):
        permission = [permission]
    else:
        if not isinstance(permission, (tuple, list)):
            raise Exception('permission must be a string, tuple or list')
    return permission


def verify_page(request):
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError as _:
        page = 1
    return page if page > 0 else 1


def get_pages(total, limit=PAGE_LIMIT):
    return int(math.ceil(total / (limit * 1.0)))


def get_offset_start_end(page, limit=PAGE_LIMIT):
    start = 0
    page = int(page)
    if page > 1:
        start = int(page - 1) * limit
    end = start + limit
    return start, end


def list_result(dj_request, result, total, page, **kwargs):
    context = {
        'result': result,
        'total': total,
        'total_pages': get_pages(total),
        'page': page,
        'permissions': get_user_default_permissions_name(dj_request)
    }
    if kwargs:
        context.update(kwargs)
    return context
