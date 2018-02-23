import threading

from django.contrib.auth.models import User
from rest_framework import serializers

from wallet.models import Wallet


def create_user(username, password, wallet_point):
    user = User.objects.create_superuser(username=username, email='', password=password)
    Wallet.objects.create(user=user, point=wallet_point)


def test_concurrently(times):
    """
    https://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/
    Add this decorator to small pieces of code that you want to test
    concurrently to make sure they don't raise exceptions when run at the
    same time.  E.g., some Django views that do a SELECT and then a subsequent
    INSERT might fail when the INSERT assumes that the data has not changed
    since the SELECT.
    """

    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []

            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception, e:
                    exceptions.append(e)
                    raise

            threads = []
            for i in range(times):
                threads.append(threading.Thread(target=call_test_func))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception('test_concurrently intercepted %s exceptions: %s' % (len(exceptions), exceptions))

        return wrapper

    return test_concurrently_decorator


class PointSerializer(serializers.Serializer):
    point = serializers.IntegerField()

    def validate_point(self, point):
        if point <= 0:
            raise serializers.ValidationError('point <= 0')
        return point
