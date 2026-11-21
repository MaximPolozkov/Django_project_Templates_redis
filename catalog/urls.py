from django.contrib.auth.decorators import login_required
from django.urls import path

from catalog.cache import cache_product_page

from catalog.views import (
    CategoryProductsView,
    ContactsView,
    HomeView,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductUnpublishView,
    ProductUpdateView,
)

app_name = "catalog"

# Список товаров открыт всем; остальные страницы товаров — только для вошедших.
# Кто именно может изменить, удалить или снять товар с публикации,
# проверяют сами контроллеры (владелец / модератор).
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path(
        "categories/<int:pk>/",
        CategoryProductsView.as_view(),
        name="category_products",
    ),
    path(
        "products/create/",
        login_required(ProductCreateView.as_view()),
        name="product_create",
    ),
    path(
        "products/<int:pk>/",
        # Страница товара кешируется в Redis (cache_page, см. catalog/cache.py)
        login_required(cache_product_page(ProductDetailView.as_view())),
        name="product_detail",
    ),
    path(
        "products/<int:pk>/update/",
        login_required(ProductUpdateView.as_view()),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        login_required(ProductDeleteView.as_view()),
        name="product_delete",
    ),
    path(
        "products/<int:pk>/unpublish/",
        login_required(ProductUnpublishView.as_view()),
        name="product_unpublish",
    ),
]
