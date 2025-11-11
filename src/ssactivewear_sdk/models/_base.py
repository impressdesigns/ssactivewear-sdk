"""Internal types."""

from pydantic import BaseModel as PydanticBaseModel


class SSActivewearBaseModel(
    PydanticBaseModel,
    strict=True,
    extra="forbid",
    frozen=True,
):
    """Custom base model for global settings."""
