
from django.dispatch import Signal

from .utils import user_operation_log_cb


operation_log_signal = Signal(providing_args=('user', 'title', 'type', 'before', 'after'))
operation_log_signal.connect(user_operation_log_cb, dispatch_uid='verdict_operation_log_signal_9527')

