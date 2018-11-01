import datetime
import math

from .config import PAGE_LIMIT


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


def get_pages(total, limit=PAGE_LIMIT):
    return int(math.ceil(total / (limit * 1.0)))


def get_offset_start_end(page, limit=PAGE_LIMIT):
    start = 0
    page = int(page)
    if page > 1:
        start = int(page - 1) * limit
    end = start + limit
    return start, end
