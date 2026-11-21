from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


def get_product_page_version_key(pk):
    return f"product_page_version_{pk}"


def cache_product_page(view):
    """Кеширует страницу товара на CACHE_TTL секунд (cache_page).

    - vary_on_cookie: у каждого пользователя своя копия страницы, потому что
      кнопки «Редактировать» / «Удалить» зависят от того, кто смотрит;
    - в key_prefix входит «версия» товара: при сохранении или удалении товара
      версия увеличивается (catalog/signals.py), и старая копия больше не отдаётся.
    """

    @wraps(view)
    def wrapper(request, pk, *args, **kwargs):
        if not settings.CACHE_ENABLED:
            return view(request, pk, *args, **kwargs)
        version = cache.get_or_set(get_product_page_version_key(pk), 1, None)
        cached_view = cache_page(
            settings.CACHE_TTL, key_prefix=f"product_{pk}_v{version}"
        )(vary_on_cookie(view))
        return cached_view(request, pk, *args, **kwargs)

    return wrapper


def invalidate_product_page(pk):
    key = get_product_page_version_key(pk)
    try:
        cache.incr(key)
    except ValueError:
        # Версии ещё нет в кеше — страница не кешировалась
        cache.set(key, 2, None)
