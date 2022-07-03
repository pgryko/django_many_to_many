from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from address_book_api.apis import PostalAddressViewSet
from address_book_api.views import index_html

router = routers.DefaultRouter()
router.register(r"", PostalAddressViewSet, basename="postaladdress")


urlpatterns = [
    path("api/v1/addressbook", include(router.urls), name="api"),
    # YOUR PATTERNS
    path("api/schema/openapi", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # For demo purposes list available urls
    path("", index_html, name="index"),
]
