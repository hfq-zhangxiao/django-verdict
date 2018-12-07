
from django.conf import settings

from .config import verdict_settings, user_model_label


cache = verdict_settings.get('CACHE', {})

if cache:
    prefix = cache.get('prefix', 'verdict')
    redis_connection = {
        'host': cache.get('host', ''),
        'port': cache.get('port', ''),
        'db': cache.get('db', ''),
        'socket_timeout': cache.get('socket_timeout', 3),
        'password': cache.get('password', ''),
    }
    cache_ops = {
        'verdict.*': {'ops': 'all', 'timeout': 60*60},
        user_model_label: {'ops': 'all', 'timeout': 60*60},
    }
    settings.CACHEOPS_REDIS = redis_connection
    settings.CACHEOPS = cache_ops
    settings.CACHEOPS_PREFIX = lambda query: '%s:' % prefix
