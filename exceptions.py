from django.core.exceptions import PermissionDenied


class NoPermissionException(PermissionDenied):
    message = 'no permission'


class NoLoginException(Exception):
    message = 'no login'


class MissingFields(Exception):
    message = 'missing fields'
