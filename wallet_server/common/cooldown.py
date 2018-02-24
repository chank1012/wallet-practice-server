from functools import wraps

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

_cooldown_redis_key_prefix = '#cooldown#'


def apply_unsafe_cooldown(lock_name=None, seconds=1.0, per_user=True):
    def decorator(f):
        @wraps(f)
        def wrapper(self, request, *args, **kwargs):
            # make key string
            if lock_name:
                key = _cooldown_redis_key_prefix + lock_name
            else:
                key = _cooldown_redis_key_prefix + self.__module__ + '.' + self.__class__.__name__ + '.' + f.__name__
            if per_user:
                if request.user.is_anonymous():
                    return Response(status=status.HTTP_403_FORBIDDEN)
                else:
                    key += '_user{}'.format(request.user.pk)
            # check lock
            if cache.get(key):
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                cache.set(key, 1, timeout=seconds)
                return f(self, request, *args, **kwargs)

        return wrapper

    return decorator


def apply_safe_cooldown(lock_name=None, seconds=1.0, per_user=True):
    def decorator(f):
        @wraps(f)
        def wrapper(self, request, *args, **kwargs):
            # make key string
            if lock_name:
                key = _cooldown_redis_key_prefix + lock_name
            else:
                key = _cooldown_redis_key_prefix + self.__module__ + '.' + self.__class__.__name__ + '.' + f.__name__
            if per_user:
                if request.user.is_anonymous():
                    return Response(status=status.HTTP_403_FORBIDDEN)
                else:
                    key += '_user{}'.format(request.user.pk)
            # check lock
            _lock = cache.lock(key, timeout=seconds)
            if _lock.acquire(blocking=False):
                return f(self, request, *args, **kwargs)
            else:
                # already locked, return error
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        return wrapper

    return decorator


def clear_all_cooldowns():
    return cache.delete_pattern(_cooldown_redis_key_prefix + '*')
