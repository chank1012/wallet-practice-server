# Wallet practice server #

안전한 point system을 구현하는 것을 연습하기 위한 django proof-of-concept 프로젝트입니다.

## Shortcut ##

`wallet/models.py`에 Wallet 모델과 여러가지 `use` 함수가 구현되어 있습니다.

`wallet/views.py`에서 `use` 함수를 호출합니다.

`wallet/tests.py`에서 각 view를 concurrent하게 호출하고, 포인트가 정상적으로 차감되었는지 검사합니다.

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
    "DATABASE_NAME": "dd"
  }
  ```

- Run `python manage.py test`

## References ##

- [Reproducing Race Conditions in Tests](http://www.informit.com/articles/article.aspx?p=1882162)

- [Testing Django Views for Concurrency Issues](https://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/)
