"""Error models."""

from pydantic import Field

from ._base import FlexibleStr, SSActivewearBaseModel


class ErrorDetail(SSActivewearBaseModel):
    """Detailed information about an error."""

    field: str = Field(
        description="Field where the error occurred.",
    )
    message: str = Field(
        description="Error message.",
    )


class ErrorResponse(SSActivewearBaseModel):
    """An error response body.

    Every field is optional: a 400 sends ``code``, ``message`` and ``errors``, a not-found 404
    sends only ``errors``, and a routing 404 sends ``message`` and ``messageDetail``.
    """

    code: FlexibleStr | None = Field(
        default=None,
        description="HTTP status code, as a string.",
    )
    message: str | None = Field(
        default=None,
        description="Error message.",
    )
    message_detail: str | None = Field(
        default=None,
        alias="messageDetail",
        description="More detail on the error.",
    )
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="Each problem with the request.",
    )

    def describe(self) -> str | None:
        """Summarize the error as one line, or ``None`` if the body carried nothing useful."""
        parts = [part for part in (self.message, self.message_detail) if part]
        parts.extend(f"{error.field}: {error.message}" for error in self.errors)
        return " ".join(parts) or None
