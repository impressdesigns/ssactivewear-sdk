"""Invoice models."""

from pydantic import Field

from ._base import SSActivewearBaseModel


class InvoicePDF(SSActivewearBaseModel):
    """An invoice document."""

    filename: str | None = Field(
        description=(
            "The file name S&S suggests: ``{warehousename}_Invoice_{invoicenumber}.pdf`` for one invoice, "
            "``{companyname}_Invoice_{ordernumber}.pdf`` for every invoice on an order."
        ),
    )
    content: bytes = Field(
        description="The PDF document.",
    )
