import time
from django.contrib.auth.models import User
from django.test import LiveServerTestCase, Client

from common.cooldown import clear_all_cooldowns
from common.counter import AtomicCounter
from common.test_utils import test_concurrently
from wallet.models import Wallet


def create_user(username, password, wallet_point):
    user = User.objects.create_superuser(username=username, email='', password=password)
    Wallet.objects.create(user=user, point=wallet_point)
    return user


class WalletConcurrencyTestCase(LiveServerTestCase):
    number_of_trials = 3
    concurrency = 5
    initial_point = 100

    def setUp(self):
        self.usernames = []
        for i in range(self.number_of_trials):
            username = 'user{}'.format(i)
            create_user(username=username, password='1234', wallet_point=self.initial_point)
            self.usernames.append(username)

    def _test(self, name, n):
        print('Running wallet {} test {}'.format(name, n))
        print('Initial point : {}, Point should be : {}'.format(self.initial_point,
                                                                self.initial_point - self.concurrency))

        url = '/api/wallet/{name}_use_{n}/'.format(name=name, n=n)

        @test_concurrently(self.concurrency)
        def use(username, password, point):
            client = Client()
            self.assertTrue(client.login(username=username, password=password), 'login failed')
            resp = client.post(url, data={'point': point})
            self.assertEqual(resp.status_code, 200, 'use failed')

        valid = 0
        invalid = 0
        for username in self.usernames:
            # test concurrently
            use(username=username, password='1234', point=1)
            # validate
            wallet = Wallet.objects.get(user__username=username)
            print('{} : {} point'.format(username, wallet.point))
            if wallet.point == self.initial_point - self.concurrency:
                valid += 1
            else:
                invalid += 1

        return valid, invalid

    def test_unsafe_1(self):
        valid, invalid = self._test(name='unsafe', n=1)
        self.assertGreater(invalid, 0, 'weired... nothing was unsuccessful')

    def test_unsafe_2(self):
        valid, invalid = self._test(name='unsafe', n=2)
        self.assertGreater(invalid, 0, 'weired... nothing was unsuccessful')

    def test_safe_1(self):
        valid, invalid = self._test(name='safe', n=1)
        self.assertEqual(invalid, 0, 'oh no... this method is not safe!')

    def test_safe_2(self):
        valid, invalid = self._test(name='safe', n=2)
        self.assertEqual(invalid, 0, 'oh no... this method is not safe!')


class CoolWalletSleepingTestCase(LiveServerTestCase):
    number_of_trials = 3
    initial_point = 100

    def setUp(self):
        clear_all_cooldowns()
        self.user = create_user(username='user', password='1234', wallet_point=self.initial_point)

    def _test_sleeping(self, period):
        print('Running cool-wallet sleeping test (period={})'.format(period))
        url = '/api/cool_wallet/safe_use/'

        valid = 0
        invalid = 0
        client = Client()
        self.assertTrue(client.login(username='user', password='1234'), 'login failed')
        for _ in range(0, self.number_of_trials):
            resp = client.post(url, data={'point': 1})
            if resp.status_code == 200:
                valid += 1
            elif resp.status_code == 429:
                invalid += 1
            else:
                raise Exception('got unexpected status code : {}'.format(resp.status_code))
            time.sleep(period)
        return valid, invalid

    def test_fast_call(self):
        valid, invalid = self._test_sleeping(period=0.1)
        self.assertEqual(valid, 1, 'cooldown did not work!')

    def test_slow_call(self):
        valid, invalid = self._test_sleeping(period=2.0)
        self.assertEqual(valid, self.number_of_trials, 'cooldown did not work!')


class CoolWalletConcurrencyTestCase(LiveServerTestCase):
    number_of_trials = 100
    concurrency = 3
    initial_point = 100

    def setUp(self):
        clear_all_cooldowns()
        self.usernames = []
        for i in range(self.number_of_trials):
            username = 'user{}'.format(i)
            create_user(username=username, password='1234', wallet_point=self.initial_point)
            self.usernames.append(username)

    def _test_concurrecy(self, name):
        print('Running cool-wallet {} concurrency test'.format(name))
        url = '/api/cool_wallet/{}_use/'.format(name)

        @test_concurrently(self.concurrency)
        def use(username, password, point, success_counter, failure_counter):
            client = Client()
            self.assertTrue(client.login(username=username, password=password), 'login failed')
            resp = client.post(url, data={'point': point})
            if resp.status_code == 200:
                success_counter.increment()
            elif resp.status_code == 429:
                failure_counter.increment()
            else:
                raise Exception('got unexpected status code : {}'.format(resp.status_code))

        valid = 0
        invalid = 0
        for username in self.usernames:
            success = AtomicCounter()
            failure = AtomicCounter()
            # test concurrently
            use(username=username, password='1234', point=1, success_counter=success, failure_counter=failure)
            # validate
            if success.value() == 1:
                valid += 1
            else:
                invalid += 1

        return valid, invalid

    def test_unsafe_concurrent_call(self):
        valid, invalid = self._test_concurrecy('unsafe')
        print('Unsafe cooldown sometimes fails with race condition... (although rare...)')
        print('Valid = {}, Invalid = {}'.format(valid, invalid))

    def test_safe_concurrent_call(self):
        valid, invalid = self._test_concurrecy('safe')
        self.assertEqual(invalid, 0, 'oh no, safe cooldown is not safe! (Invalid = {})'.format(invalid))
