"""Return models."""

from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from ._base import FlexibleBool, SSActivewearBaseModel
from .orders import Order


class ReturnReason(StrEnum):
    """Reasons accepted when requesting a return."""

    DO_NOT_NEED = "1"
    """Do not need; ordered the wrong color, size, or quantity."""
    DAMAGED_OR_DEFECTIVE = "2"
    """Damaged or defective item. Needs a comment when replacing."""
    KEYING_ERROR = "3"
    """Keying error (ordered X, billed and received Y)."""
    RECEIVED_TOO_FEW = "5"
    """Wrong quantity (ordered 10, received 2)."""
    OTHER = "6"
    """Other. Needs a comment when replacing."""
    RECEIVED_TOO_MANY = "7"
    """Wrong quantity (ordered 2, received 10)."""
    PICKING_ERROR_WRONG_SIZE = "10"
    """Picking error (wrong size)."""
    PICKING_ERROR_WRONG_STYLE_OR_COLOR = "11"
    """Picking error (wrong style or color)."""


REASONS_REQUIRING_A_COMMENT = frozenset({ReturnReason.DAMAGED_OR_DEFECTIVE, ReturnReason.OTHER})


class ReturnRequestLine(SSActivewearBaseModel):
    """A sku to return."""

    invoice_number: str = Field(
        alias="invoiceNumber",
        description="Invoice the sku was billed on.",
    )
    identifier: str = Field(
        description="SkuID, Sku, or Gtin.",
    )
    qty: int = Field(
        description="Quantity to return.",
    )
    return_reason: ReturnReason = Field(
        alias="returnReason",
        description="Why the sku is being returned.",
    )
    is_replace: bool | None = Field(
        default=None,
        alias="isReplace",
        description="Ship a replacement. S&S defaults to false.",
    )
    return_reason_comment: str | None = Field(
        default=None,
        alias="returnReasonComment",
        description="Required when replacing a damaged or defective item, or for the other reason.",
    )

    @model_validator(mode="after")
    def _require_comment_for_replacements(self) -> Self:
        """S&S rejects a replacement for reason 2 or 6 without a comment."""
        if (
            self.is_replace
            and self.return_reason in REASONS_REQUIRING_A_COMMENT
            and not (self.return_reason_comment and self.return_reason_comment.strip())
        ):
            message = f"return_reason_comment is required to replace an item returned for reason {self.return_reason}."
            raise ValueError(message)
        return self


class ReturnRequest(SSActivewearBaseModel):
    """A return to request.

    Every optional field left as ``None`` is omitted from the request, so S&S applies its own
    default.
    """

    lines: list[ReturnRequestLine] = Field(
        description="Skus to return.",
    )
    email_confirmation: str | None = Field(
        default=None,
        alias="emailConfirmation",
        description="Email address to send a confirmation to.",
    )
    test_order: bool | None = Field(
        default=None,
        alias="testOrder",
        description="Test orders are created and then cancelled.",
    )
    shipping_label_required: bool | None = Field(
        default=None,
        alias="shippingLabelRequired",
        description="Whether a return shipping label is needed. S&S defaults to true.",
    )
    show_boxes: bool | None = Field(
        default=None,
        alias="showBoxes",
        description="Include box level information in the response. S&S defaults to false.",
    )


class ReturnToAddress(SSActivewearBaseModel):
    """Where to send returned items."""

    attn: str = Field(
        description="Attention line.",
    )
    address: str = Field(
        description="Address line.",
    )
    city: str = Field(
        description="City.",
    )
    state: str = Field(
        description="State.",
    )
    zip: str = Field(
        description="ZIP code.",
    )


class ReturnInformation(SSActivewearBaseModel):
    """Details of a return order."""

    shipping_label_url: str | None = Field(
        default=None,
        alias="shippingLabelURL",
        description="Shipping label URL for the entire return order.",
    )
    return_items_required: FlexibleBool | None = Field(
        default=None,
        alias="returnItemsRequired",
        description="Whether the items need to be sent back.",
    )
    return_to_address: ReturnToAddress | None = Field(
        default=None,
        alias="returnToAddress",
        description="Where to send the items.",
    )
    ra_number: str = Field(
        alias="raNumber",
        description="Return order number.",
    )
    original_invoice: str = Field(
        alias="originalInvoice",
        description="Original invoice number. Comma separated when several invoices are involved.",
    )
    return_reason: str = Field(
        alias="returnReason",
        description="Reason for the return.",
    )

    @property
    def original_invoices(self) -> list[str]:
        """The invoice numbers in :attr:`original_invoice`, split apart."""
        return [invoice.strip() for invoice in self.original_invoice.split(",") if invoice.strip()]


class ReturnOrder(Order):
    """A return (credit) or replacement order.

    Credit orders have an ``order_type`` of ``Credit``; replacement orders have ``Replacement``.
    """

    return_information: ReturnInformation | None = Field(
        default=None,
        alias="returnInformation",
        description="Details of the return.",
    )
