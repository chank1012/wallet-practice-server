import time
from django.contrib.auth.models import User
from django.test import LiveServerTestCase, Client

from common.cooldown import clear_all_cooldowns
from common.test_utils import test_concurrently
from wallet.models import Wallet


def create_user(username, password, wallet_point):
    user = User.objects.create_superuser(username=username, email='', password=password)
    Wallet.objects.create(user=user, point=wallet_point)
    return user


class WalletTestCase(LiveServerTestCase):
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
            assert client.login(username=username, password=password), 'login failed'
            resp = client.post(url, data={'point': point})
            assert resp.status_code == 200, 'use failed'

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
        assert invalid > 0, 'weired... nothing was unsuccessful'

    def test_unsafe_2(self):
        valid, invalid = self._test(name='unsafe', n=2)
        assert invalid > 0, 'weired... nothing was unsuccessful'

    def test_safe_1(self):
        valid, invalid = self._test(name='safe', n=1)
        assert invalid == 0, 'oh no... this method is not safe!'

    def test_safe_2(self):
        valid, invalid = self._test(name='safe', n=2)
        assert invalid == 0, 'oh no... this method is not safe!'


class CoolWalletTestCase(LiveServerTestCase):
    number_of_trials = 3
    initial_point = 100
    url = '/api/cool_wallet/safe_use_1/'

    def setUp(self):
        clear_all_cooldowns()
        self.user = create_user(username='user', password='1234', wallet_point=self.initial_point)

    def _test(self, period):
        print('Running cool-wallet test (period={})'.format(period))
        valid = 0
        invalid = 0
        client = Client()
        assert client.login(username='user', password='1234'), 'login failed'
        for _ in range(0, self.number_of_trials):
            resp = client.post(self.url, data={'point': 1})
            if resp.status_code == 200:
                valid += 1
            elif resp.status_code == 429:
                invalid += 1
            else:
                raise Exception('got unexpected status code : {}'.format(resp.status_code))
            time.sleep(period)
        return valid, invalid

    def test_fast_call(self):
        valid, invalid = self._test(period=0.1)
        assert valid == 1, 'cooldown did not work!'

    def test_slow_call(self):
        valid, invalid = self._test(period=2.0)
        assert valid == self.number_of_trials, 'cooldown did not work!'
