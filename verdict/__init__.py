
from django.conf import settings


user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
cache = getattr(settings, 'CACHE', {})

if cache:
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
