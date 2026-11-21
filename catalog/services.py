from django.conf import settings
from django.core.cache import cache

from catalog.models import Product


def get_category_cache_key(category_id):
    return f"category_{category_id}"


def get_products_by_category(category_id):
    """Возвращает список опубликованных товаров категории.

    Список кешируется в Redis по ключу category_{id} на CACHE_TTL секунд.
    При изменении товаров ключ сбрасывается (см. catalog/signals.py).
    """
    if not settings.CACHE_ENABLED:
        return _load_products(category_id)

    key = get_category_cache_key(category_id)
    products = cache.get(key)
    if products is None:
        products = _load_products(category_id)
        cache.set(key, products, settings.CACHE_TTL)
    return products


def _load_products(category_id):
    return list(
        Product.objects.filter(category_id=category_id, is_published=True)
        .select_related("category", "owner")
        .order_by("name")
    )


def invalidate_category_cache(*category_ids):
    keys = [get_category_cache_key(pk) for pk in category_ids if pk]
    if keys:
        cache.delete_many(keys)
