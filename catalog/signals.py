from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from catalog.cache import invalidate_product_page
from catalog.models import Product
from catalog.services import invalidate_category_cache


@receiver(pre_save, sender=Product)
def remember_old_category(sender, instance, **kwargs):
    """Запоминаем прежнюю категорию, чтобы сбросить кеш и у неё."""
    if instance.pk:
        instance._old_category_id = (
            Product.objects.filter(pk=instance.pk)
            .values_list("category_id", flat=True)
            .first()
        )
    else:
        instance._old_category_id = None


@receiver(post_save, sender=Product)
def clear_cache_on_save(sender, instance, **kwargs):
    invalidate_category_cache(instance.category_id, getattr(instance, "_old_category_id", None))
    invalidate_product_page(instance.pk)


@receiver(post_delete, sender=Product)
def clear_cache_on_delete(sender, instance, **kwargs):
    invalidate_category_cache(instance.category_id)
    invalidate_product_page(instance.pk)
