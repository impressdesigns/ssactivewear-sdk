"""Interacting with S&S' API."""

import uuid
from http import HTTPStatus
from typing import Any

from httpx import Client

from .exceptions import SSActivewearBadRequestError
from .models import ErrorResponse, OrderRequest, OrderResponseContainer, Product


class SSActivewear:
    """A class wrapping S&S' API."""

    def __init__(
        self,
        account_number: str,
        token: str,
        base_url: str = "https://api.ssactivewear.com/v2",
    ) -> None:
        try:
            int(account_number)
        except ValueError as exception:
            msg = "Account number is not a valid number!"
            raise TypeError(msg) from exception

        try:
            uuid.UUID(token)
        except ValueError as exception:
            msg = "Token is not a valid UUID!"
            raise TypeError(msg) from exception

        self.http_client = Client(base_url=base_url, auth=(account_number, token))

    def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Make a request to SSActivewear."""
        request = self.http_client.build_request(
            method=method,
            url=path,
            params=params,
            json=json,
            timeout=timeout,
        )
        response = self.http_client.send(request)

        if response.status_code == HTTPStatus.BAD_REQUEST:
            error_response = ErrorResponse.model_validate(response.json())
            raise SSActivewearBadRequestError(error_response.message, error_response)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def products(self) -> list[Product]:
        """Get all products."""
        product_data = self._make_request("GET", "/products", timeout=500)
        return [Product.model_validate(dict_) for dict_ in product_data]

    def submit_order(self, order_request: OrderRequest) -> OrderResponseContainer:
        """Submit an order to S&S Activewear."""
        response_data = self._make_request(
            method="POST",
            path="/orders",
            json=order_request.model_dump(mode="json", exclude_none=True, by_alias=True, exclude_unset=True),
        )

        if order_request.reject_line_errors:
            response_data = {
                "lineErrors": [],
                "orders": response_data,
            }

        return OrderResponseContainer.model_validate(response_data)
