"""A wrapper for S&S' API."""

from .client import SSActivewear
from .exceptions import SSActivewearBadRequestError, SSActivewearError
from .models import (
    OrderRequest,
    OrderRequestOrderLine,
    OrderRequestPaymentProfile,
    OrderRequestShippingAddress,
    OrderResponse,
    OrderResponseLine,
    OrderResponseShippingAddress,
    Product,
    Warehouse,
)

__all__ = [
    "OrderRequest",
    "OrderRequestOrderLine",
    "OrderRequestPaymentProfile",
    "OrderRequestShippingAddress",
    "OrderResponse",
    "OrderResponseLine",
    "OrderResponseShippingAddress",
    "Product",
    "SSActivewear",
    "SSActivewearBadRequestError",
    "SSActivewearError",
    "Warehouse",
]
