from django.test import LiveServerTestCase, Client

from common import create_user, test_concurrently
from wallet.models import Wallet


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
        print('Running : {} test {}'.format(name, n))
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
