
from django.conf import settings

from .config import verdict_settings, user_model_label


cache = verdict_settings.get('CACHE', {})

if cache:
    prefix = cache.get('prefix', 'verdict')
    timeout = cache.get('timeout', 60 * 60)
    redis_connection = {
        'host': cache.get('host', ''),
        'port': cache.get('port', ''),
        'db': cache.get('db', ''),
        'socket_timeout': cache.get('socket_timeout', 3),
        'password': cache.get('password', ''),
    }
    cache_ops = {
        'verdict.*': {'ops': 'all'},
        user_model_label: {'ops': 'all'},
    }
    cache_ops_default = {'timeout': timeout}
    settings.CACHEOPS_REDIS = redis_connection
    settings.CACHEOPS = cache_ops
    settings.CACHEOPS_DEFAULTS = cache_ops_default
    settings.CACHEOPS_PREFIX = lambda query: '%s:' % prefix
