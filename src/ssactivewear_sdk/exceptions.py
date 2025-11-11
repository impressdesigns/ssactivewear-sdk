"""Exceptions."""

from .models import ErrorResponse


class SSActivewearError(Exception):
    """Base exception for SSActivewear SDK errors."""


class SSActivewearBadRequestError(SSActivewearError):
    """Exception raised for bad requests to SSActivewear API."""

    def __init__(self, message: str, response: ErrorResponse) -> None:
        super().__init__(message)

        self.response = response
