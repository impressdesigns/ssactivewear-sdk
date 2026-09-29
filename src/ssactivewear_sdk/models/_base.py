"""Internal types."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel as PydanticBaseModel
from pydantic import BeforeValidator, Strict


class SSActivewearBaseModel(
    PydanticBaseModel,
    strict=True,
    frozen=True,
    validate_by_name=True,
    validate_by_alias=True,
    serialize_by_alias=True,
):
    """Custom base model for global settings.

    Unknown fields are ignored rather than rejected: S&S adds fields to its payloads over
    time, and a new field must not break parsing of everything else.
    """


def _blank_to_none(value: object) -> object:
    """Treat an empty string as a missing value."""
    if value == "":
        return None
    return value


def _number_to_str(value: object) -> object:
    """Accept a number where a string identifier is expected."""
    if isinstance(value, int | float) and not isinstance(value, bool):
        return str(value)
    return value


def _parse_timestamp(value: object) -> object:
    """Accept ISO 8601 or ``MM/DD/YYYY``, and a blank string as missing.

    A value that matches neither format is passed through unchanged so that validation
    reports it.
    """
    if value == "":
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
        try:
            return datetime.strptime(value, "%m/%d/%Y")  # noqa: DTZ007 - S&S sends naive local dates
        except ValueError:
            return value
    return value


# The published documentation contradicts itself on the types below. Each alias accepts every
# shape the documentation shows, so a response parses whichever one S&S actually sends.
# See ``docs/api-corrections.rst`` for the individual cases.

type FlexibleInt = Annotated[int, Strict(strict=False)]
"""An integer that may also arrive as a numeric string or an integral float (``-20.00``)."""

type OptionalFlexibleInt = Annotated[FlexibleInt | None, BeforeValidator(_blank_to_none)]
"""A :data:`FlexibleInt` that may also be missing, ``null``, or an empty string."""

type FlexibleBool = Annotated[bool, Strict(strict=False)]
"""A boolean that may also arrive as the string ``"true"`` or ``"false"``."""

type FlexibleStr = Annotated[str, BeforeValidator(_number_to_str)]
"""A string identifier that may also arrive as a number."""

type FlexibleDatetime = Annotated[datetime | None, BeforeValidator(_parse_timestamp)]
"""A timestamp in ISO 8601 or ``MM/DD/YYYY`` form, or empty."""
