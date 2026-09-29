"""Exceptions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ErrorResponse


class SSActivewearError(Exception):
    """Base exception for SSActivewear SDK errors."""


class SSActivewearAPIError(SSActivewearError):
    """S&S answered with an error status."""

    def __init__(self, message: str, *, status_code: int, response: ErrorResponse | None) -> None:
        super().__init__(message)

        self.status_code = status_code
        """The HTTP status code."""
        self.response = response
        """The parsed error body, or ``None`` when the body was not a recognizable error."""


class SSActivewearBadRequestError(SSActivewearAPIError):
    """S&S rejected the request (HTTP 400). ``response.errors`` lists each problem."""


class SSActivewearNotFoundError(SSActivewearAPIError):
    """Nothing matched the request, or the items were discontinued (HTTP 404)."""
