"""Error models."""

from pydantic import Field

from ._base import SSActivewearBaseModel


class ErrorDetail(SSActivewearBaseModel):
    """Detailed information about an error."""

    field: str = Field(description="Field where the error occurred")
    message: str = Field(description="Error message")


class ErrorResponse(SSActivewearBaseModel):
    """Error response model."""

    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    errors: list[ErrorDetail] = Field(description="List of errors")
