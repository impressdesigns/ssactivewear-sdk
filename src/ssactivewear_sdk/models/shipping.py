"""Shipping models: days in transit and tracking."""

from pydantic import Field

from ._base import FlexibleDatetime, FlexibleStr, OptionalFlexibleInt, SSActivewearBaseModel


class WarehouseTransit(SSActivewearBaseModel):
    """Cutoff time and transit time from one warehouse."""

    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Code identifying the warehouse.",
    )
    cut_off_time: str = Field(
        alias="cutOffTime",
        description="Time an order must be placed by to ship the same day, e.g. 4:00 CT.",
    )
    time_period: str = Field(
        alias="timePeriod",
        description="AM or PM.",
    )
    cut_off_time_24hr: str = Field(
        alias="cutOffTime24hr",
        description="Time an order must be placed by to ship the same day, 24 hour format.",
    )
    days_in_transit: int = Field(
        alias="daysInTransit",
        description="Days it takes for an order to be delivered.",
    )


class DaysInTransit(SSActivewearBaseModel):
    """Transit times from each warehouse to a ZIP code."""

    zip_code: str = Field(
        alias="zipCode",
        description="ZIP code.",
    )
    warehouses: list[WarehouseTransit] = Field(
        default_factory=list,
        description="Transit time from each warehouse.",
    )


class TrackingCheckpoint(SSActivewearBaseModel):
    """The most recent carrier scan of a shipment.

    S&S does not document this object, so every field is optional.
    """

    checkpoint_date: str | None = Field(
        default=None,
        alias="checkpointDate",
        description="Date of the scan, e.g. 5/10/2021.",
    )
    checkpoint_time: str | None = Field(
        default=None,
        alias="checkpointTime",
        description="Time of the scan, e.g. 4:11 PM.",
    )
    checkpoint_location: str | None = Field(
        default=None,
        alias="checkpointLocation",
        description="Where the scan happened.",
    )
    checkpoint_status_message: str | None = Field(
        default=None,
        alias="checkpointStatusMessage",
        description="The carrier's status message.",
    )


class TrackingData(SSActivewearBaseModel):
    """The shipping status of a package.

    S&S does not document this object, so every field is optional.
    """

    carrier_name: str | None = Field(
        default=None,
        alias="carrierName",
        description="Carrier, e.g. UPS or USPS.",
    )
    tracking_number: str | None = Field(
        default=None,
        alias="trackingNumber",
        description="Tracking number.",
    )
    origin: str | None = Field(
        default=None,
        description="Where the package shipped from.",
    )
    actual_delivery_date_time: FlexibleDatetime = Field(
        default=None,
        alias="actualDeliveryDateTime",
        description="When the package was delivered.",
    )
    signed_by: str | None = Field(
        default=None,
        alias="signedBy",
        description="Who signed for the package.",
    )
    latest_checkpoint: TrackingCheckpoint | None = Field(
        default=None,
        alias="latestCheckpoint",
        description="The most recent carrier scan.",
    )
    order_number: FlexibleStr | None = Field(
        default=None,
        alias="orderNumber",
        description="Order number.",
    )
    invoice_number: FlexibleStr | None = Field(
        default=None,
        alias="invoiceNumber",
        description="Invoice number.",
    )
    box_number: OptionalFlexibleInt = Field(
        default=None,
        alias="boxNumber",
        description="Box number. Only sent when boxes were requested and the shipment has several boxes.",
    )
