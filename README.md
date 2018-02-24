# Wallet practice server #

안전한 point system을 구현하는 것을 연습하기 위한 django proof-of-concept 프로젝트입니다.

## Shortcut ##

### (1) Wallet test ###

API를 동시에 여러 번 호출하였을 때, point가 정상적으로 차감되는지 테스트합니다.

`wallet/models.py`에 Wallet 모델과 여러가지 `use` 함수가 구현되어 있습니다.

`wallet/views.py`에 `use` 함수를 호출하는 API가 구현되어 있습니다.

`wallet/tests.py`에서 각 API를 concurrent하게 호출하고, 포인트가 정상적으로 차감되었는지 검사합니다.

- unsafe tests : 올바르게 구현하지 않은 경우, 오류 발생

- safe tests : 올바르게 구현하였으므로, 오류 없음

### (2) Cool wallet test ###

API에 Cooldown(연속해서 호출할 수 없도록 minimum period를 두는 기능)을 적용하여 정상적으로 작동하는지 테스트합니다.

`common/cooldown.py`에 `apply_cooldown` decorator가 구현되어 있습니다.

`wallet/views.py`에 Cooldown이 적용된 API가 구현되어 있습니다.

`wallet/tests.py`에서 API를 호출하고, Cooldown이 정상작동하는지 테스트합니다.

- unsafe cooldown :

  ```
  if cache.get(key):
    fail
  else:
    cache.set(key, 1, timeout)
  ```

  실험 결과 : 약 5% 의 확률로 오작동

- safe cooldown :

  ```
  if lock.acquire(key):
    success
  else:
    fail
  ```

  실험 결과 : 약 0.5%의 확률로 오작동

## Important things ##

- test driven!

- reproduce race condition at `unsafe` tests, solve it at `safe` tests

  - reproducibility is non-deterministic but likely

## How to test ##

- Configure `wallet_server/secret.json`

  ```
  {
    "DATABASE_HOST": "aa",
    "DATABASE_USER": "bb",
    "DATABASE_PASSWORD": "cc",
    "DATABASE_NAME": "dd",
    "REDIS_LOCATION": "redis://127.0.0.1:6379/1",
    "REDIS_KEY_PREFIX": "wallet"
  }
  ```

- Run `python manage.py test`

## References ##

- [Reproducing Race Conditions in Tests](http://www.informit.com/articles/article.aspx?p=1882162)

- [Testing Django Views for Concurrency Issues](https://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/)
