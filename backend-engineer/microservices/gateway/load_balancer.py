import itertools
import os
USER_SERVICE_URLS = os.getenv("USER_SERVICE_URLS", "http://user_service:8000").split(",")
PRODUCT_SERVICE_URLS = os.getenv("PRODUCT_SERVICE_URLS", "http://product_service:8000").split(",")
ORDER_SERVICE_URLS = os.getenv("ORDER_SERVICE_URLS", "http://order_service:8000").split(",")

service_pools = {
    "user_service": itertools.cycle(USER_SERVICE_URLS),
    "product_service": itertools.cycle(PRODUCT_SERVICE_URLS),
    "order_service": itertools.cycle(ORDER_SERVICE_URLS),
}


def get_service_url(service_name: str) -> str:
    return next(service_pools[service_name])
