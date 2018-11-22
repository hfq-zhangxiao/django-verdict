from django.core.exceptions import PermissionDenied


class NoPermissionException(PermissionDenied):
    message = 'no permission'


class NoLoginException(Exception):
    status_code = 400


class MissingFields(Exception):
    message = 'missing fields'
