"""Order models."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import AliasChoices, Field, JsonValue, field_serializer

from ._base import FlexibleInt, SSActivewearBaseModel


class ShippingMethod(StrEnum):
    """Shipping methods accepted when placing an order."""

    GROUND = "1"
    """Ground (carrier determined by S&S)."""
    UPS_NEXT_DAY_AIR = "2"
    UPS_SECOND_DAY_AIR = "3"
    WILL_CALL = "6"
    """Will call / pickup."""
    MESSENGER_PICKUP = "8"
    """Messenger pickup / pickup."""
    FEDEX_GROUND = "14"
    UPS_THREE_DAY_SELECT = "16"
    UPS_NEXT_DAY_AIR_EARLY_AM = "17"
    UPS_SATURDAY = "19"
    UPS_SATURDAY_EARLY = "20"
    UPS_NEXT_DAY_AIR_SAVER = "21"
    UPS_SECOND_DAY_AIR_AM = "22"
    FEDEX_NEXT_DAY_PRIORITY = "26"
    FEDEX_NEXT_DAY_STANDARD = "27"
    UPS_GROUND = "40"
    FEDEX_SECOND_DAY_AIR = "48"
    MISC_CHEAPEST = "54"
    """S&S picks the most cost-effective ground service (USPS First Class, USPS Priority Mail, UPS SurePost, UPS Ground)."""  # noqa: E501


# ---------------------------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------------------------


class OrderShippingAddress(SSActivewearBaseModel):
    """Where to ship an order."""

    address: str = Field(
        description="Street address.",
    )
    city: str = Field(
        description="City.",
    )
    state: str = Field(
        description="State abbreviation.",
    )
    zip: str = Field(
        description="ZIP code (5 digits).",
    )
    customer: str | None = Field(
        default=None,
        description='Customer or company name. S&S defaults to "".',
    )
    attn: str | None = Field(
        default=None,
        description='Attention line. S&S defaults to "".',
    )
    residential: bool | None = Field(
        default=None,
        description="Whether this is a residential address. S&S defaults to true.",
    )


class OrderLineRequest(SSActivewearBaseModel):
    """A sku to order."""

    identifier: str = Field(
        description="SkuID_Master, Sku, or Gtin.",
    )
    qty: int = Field(
        description="Quantity to order.",
    )
    warehouse_abbr: str | None = Field(
        default=None,
        alias="warehouseAbbr",
        description="Warehouse to ship from. Ignored when ``autoselect_warehouse`` is set.",
    )


class PaymentProfileReference(SSActivewearBaseModel):
    """A saved credit card or bank account to pay with."""

    email: str = Field(
        description="Email of the website user the payment method is saved under.",
    )
    profile_id: int = Field(
        alias="profileID",
        description="Profile ID returned by :meth:`~ssactivewear_sdk.client.SSActivewear.get_payment_profiles`.",
    )


class OrderRequest(SSActivewearBaseModel):
    """An order to place.

    Every optional field left as ``None`` is omitted from the request, so S&S applies its own
    default.
    """

    shipping_address: OrderShippingAddress = Field(
        alias="shippingAddress",
        description="Where to ship the order.",
    )
    lines: list[OrderLineRequest] = Field(
        description="Skus to order.",
    )
    shipping_method: ShippingMethod | None = Field(
        default=None,
        alias="shippingMethod",
        description="Shipping method. S&S defaults to ground.",
    )
    ship_blind: bool | None = Field(
        default=None,
        alias="shipBlind",
        description="Overrides the account's blind shipping setting.",
    )
    po_number: str | None = Field(
        default=None,
        alias="poNumber",
        description="Customer PO number.",
    )
    email_confirmation: str | None = Field(
        default=None,
        alias="emailConfirmation",
        description="Email address to send an order confirmation to.",
    )
    test_order: bool | None = Field(
        default=None,
        alias="testOrder",
        description="Test orders are created and then cancelled.",
    )
    autoselect_warehouse: bool | None = Field(
        default=None,
        alias="autoselectWarehouse",
        description="Let S&S choose the warehouse. Lines may be split between warehouses.",
    )
    promotion_code: str | None = Field(
        default=None,
        alias="promotionCode",
        description="Promotion code that applies to products on the order.",
    )
    autoselect_warehouse_warehouses: list[str] | None = Field(
        default=None,
        alias="autoselectWarehouse_Warehouses",
        description="Restrict warehouse autoselection to these warehouses.",
    )
    autoselect_warehouse_preference: Literal["fewest", "fastest"] | None = Field(
        default=None,
        alias="AutoSelectWarehouse_Preference",
        description="Freight optimizer selection. S&S defaults to fewest.",
    )
    autoselect_warehouse_fewest_max_dit: int | None = Field(
        default=None,
        alias="AutoSelectWarehouse_Fewest_MaxDIT",
        description="Maximum days in transit for fewest before switching to fastest. S&S defaults to 10.",
    )
    reject_line_errors: bool | None = Field(
        default=None,
        alias="rejectLineErrors",
        description=(
            "When false, S&S places the order for every line it can fill and reports the rest as "
            "line errors. S&S defaults to true."
        ),
    )
    reject_line_errors_email: bool | None = Field(
        default=None,
        alias="rejectLineErrors_Email",
        description="Email unfillable lines to ``email_confirmation``. S&S defaults to true.",
    )
    payment_profile: PaymentProfileReference | None = Field(
        default=None,
        alias="paymentProfile",
        description="Pay with a saved credit card or bank account.",
    )
    ship_by_date: date | None = Field(
        default=None,
        alias="shipByDate",
        description="Ship by date.",
    )

    @field_serializer("autoselect_warehouse_warehouses")
    def _serialize_warehouses(self, warehouses: list[str] | None) -> str | None:
        """S&S takes the warehouse list as one comma separated string."""
        if warehouses is None:
            return None
        return ",".join(warehouses)

    @field_serializer("ship_by_date")
    def _serialize_ship_by_date(self, ship_by_date: date | None) -> str | None:
        """S&S takes the ship by date as ``MM/DD/YYYY``."""
        if ship_by_date is None:
            return None
        return ship_by_date.strftime("%m/%d/%Y")


# ---------------------------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------------------------


class ShippingAddress(SSActivewearBaseModel):
    """Where an order ships to."""

    customer: str = Field(
        description="Customer name.",
    )
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


class BillingAddress(SSActivewearBaseModel):
    """Who an order is billed to."""

    bill_to: str = Field(
        alias="billTo",
        description="Billing name.",
    )
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


class OrderLine(SSActivewearBaseModel):
    """A line of an order, or of a box within an order."""

    line_number: int = Field(
        alias="lineNumber",
        description="Line number of the order.",
    )
    type: str = Field(
        description="S = stocked skus, NS = not stocked skus.",
    )
    sku_id: int = Field(
        alias="skuID",
        description="Unique ID for this sku (does not change).",
    )
    sku: str = Field(
        description="Part number for the product.",
    )
    gtin: str = Field(
        description="Industry standard identifier used by all suppliers.",
    )
    your_sku: str = Field(
        alias="yourSku",
        description="Your sku, set up using the cross reference API.",
    )
    qty_ordered: FlexibleInt = Field(
        alias="qtyOrdered",
        description="Quantity ordered. Negative on return (credit) orders.",
    )
    qty_shipped: int | None = Field(
        default=None,
        alias="qtyShipped",
        description="Quantity shipped.",
    )
    price: Decimal | None = Field(
        default=None,
        description="Price of each item. Not sent on box lines.",
    )
    brand_name: str = Field(
        alias="brandName",
        description="Brand name.",
    )
    style_name: str = Field(
        alias="styleName",
        description="Style name.",
    )
    title: str = Field(
        description="Description of the product.",
    )
    color_name: str = Field(
        alias="colorName",
        description="Color name.",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size name.",
    )
    returnable: bool | None = Field(
        default=None,
        description="This product is eligible for return. Not sent on box lines.",
    )


class BoxReturnInformation(SSActivewearBaseModel):
    """Return shipping labels for one box of a return order."""

    shipping_label_png: str | None = Field(
        default=None,
        alias="shippingLabelPNG",
        description="Shipping label URL for the box.",
    )
    shipping_label_zpl: str | None = Field(
        default=None,
        alias="shippingLabelZPL",
        description="Base64 encoded ZPL code for the box.",
    )


class Box(SSActivewearBaseModel):
    """A box in a shipment."""

    box_number: int = Field(
        alias="boxNumber",
        description="Box number of the order.",
    )
    tracking_number: str = Field(
        alias="trackingNumber",
        description="Tracking number.",
    )
    weight: Decimal = Field(
        description="Weight of the box.",
    )
    cubic_volume: Decimal = Field(
        alias="cubicVolume",
        description="Cubic volume of the box.",
    )
    box_required: bool | None = Field(
        default=None,
        alias="boxRequired",
        description="Undocumented by S&S.",
    )
    conveyor_barcode: str | None = Field(
        default=None,
        alias="conveyorBarcode",
        description="Conveyor barcode.",
    )
    return_information: BoxReturnInformation | None = Field(
        default=None,
        alias="returnInformation",
        description="Return shipping labels. Only sent for return orders.",
    )
    lines: list[OrderLine] = Field(
        default_factory=list,
        description="Lines packed in this box.",
    )


class Order(SSActivewearBaseModel):
    """A placed order.

    Totals and lines are only as complete as the request asked for: ``lines``, ``boxes`` and
    ``billing_address`` are only sent when requested, and ``ship_date``, ``invoice_date`` and
    ``tracking_number`` only once the order has shipped or been invoiced.
    """

    guid: UUID = Field(
        description="Unique ID for this order (does not change).",
    )
    company_name: str = Field(
        alias="companyName",
        description="Company name.",
    )
    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Warehouse the order ships from.",
    )
    order_number: str = Field(
        alias="orderNumber",
        description="The order and confirmation number assigned when the order was placed.",
    )
    invoice_number: str = Field(
        alias="invoiceNumber",
        description="The invoice number, assigned shortly after the order is placed.",
    )
    po_number: str = Field(
        alias="poNumber",
        description="The PO number submitted with the order.",
    )
    customer_number: str = Field(
        alias="customerNumber",
        description="Customer number of the account.",
    )
    order_header_id: int | None = Field(
        default=None,
        alias="orderHeaderID",
        description="Undocumented by S&S; present in its code samples.",
    )
    order_date: datetime = Field(
        alias="orderDate",
        description="When the order was placed.",
    )
    ship_date: datetime | None = Field(
        default=None,
        alias="shipDate",
        description="When the order shipped.",
    )
    invoice_date: datetime | None = Field(
        default=None,
        alias="invoiceDate",
        description="When the order was invoiced.",
    )
    expected_delivery_date: datetime | None = Field(
        default=None,
        alias="expectedDeliveryDate",
        description="When the order is expected to be delivered.",
    )
    order_type: str = Field(
        alias="orderType",
        description="How the order was placed, e.g. CSR, Web, EDI, API, Credit, Replacement.",
    )
    terms: str = Field(
        description="Terms of the order.",
    )
    order_status: str = Field(
        alias="orderStatus",
        description="Status of the order, e.g. In Progress, Shipped, Completed, Cancelled.",
    )
    dropship: bool = Field(
        description="If the order is a dropship order.",
    )
    shipping_carrier: str = Field(
        alias="shippingCarrier",
        description="Carrier used.",
    )
    shipping_method: str = Field(
        alias="shippingMethod",
        description="Freight service used.",
    )
    ship_blind: bool = Field(
        alias="shipBlind",
        description="If the order ships blind.",
    )
    shipping_collect_number: str = Field(
        alias="shippingCollectNumber",
        description="Freight account that was charged.",
    )
    tracking_number: str | None = Field(
        default=None,
        alias="trackingNumber",
        description="Tracking number.",
    )
    shipping_address: ShippingAddress = Field(
        alias="shippingAddress",
        description="Where the order ships to.",
    )
    billing_address: BillingAddress | None = Field(
        default=None,
        alias="billingAddress",
        description="Who the order is billed to.",
    )
    subtotal: Decimal = Field(
        description="Merchandise value of the order.",
    )
    shipping: Decimal = Field(
        description="Shipping and handling charged.",
    )
    shipping_saved: Decimal | None = Field(
        default=None,
        alias="shippingSaved",
        description="Difference between the carrier's cost for the shipment and what S&S charged.",
    )
    cod: Decimal = Field(
        description="COD amount.",
    )
    tax: Decimal = Field(
        description="Tax charged.",
    )
    lost_cash_discount: Decimal | None = Field(
        default=None,
        alias="lostCashDiscount",
        description="Lost cash discount.",
    )
    small_order_fee: Decimal = Field(
        alias="smallOrderFee",
        description="Small order fee.",
    )
    cupon_discount: Decimal = Field(
        alias="cuponDiscount",
        description="Miscellaneous discount (not used).",
    )
    sample_discount: Decimal = Field(
        alias="sampleDiscount",
        description="Sample discount.",
    )
    set_up_fee: Decimal = Field(
        alias="setUpFee",
        description="Set up fee.",
    )
    restock_fee: Decimal = Field(
        alias="restockFee",
        description="Restock fee.",
    )
    debit_credit: Decimal = Field(
        alias="debitCredit",
        description="Debit/credit.",
    )
    total: Decimal = Field(
        description="Total order amount.",
    )
    total_pieces: FlexibleInt = Field(
        alias="totalPieces",
        description="Total pieces on the order. Negative on return (credit) orders.",
    )
    total_lines: int = Field(
        alias="totalLines",
        description="Total lines on the order.",
    )
    total_weight: Decimal = Field(
        alias="totalWeight",
        description="Total weight of the order.",
    )
    total_boxes: FlexibleInt = Field(
        alias="totalBoxes",
        description="Total boxes on the order.",
    )
    delivery_status: str | None = Field(
        default=None,
        alias="deliveryStatus",
        description="Current delivery status, e.g. Shipped - In Transit.",
    )
    conveyor_lane: str | None = Field(
        default=None,
        alias="conveyorLane",
        description="Conveyor lane.",
    )
    lines: list[OrderLine] = Field(
        default_factory=list,
        description="Order lines. Only sent when requested.",
    )
    boxes: list[Box] = Field(
        default_factory=list,
        description="Boxes in the shipment. Only sent when requested.",
    )


class OrderSubmission(SSActivewearBaseModel):
    """The result of placing an order.

    An order may be split into several orders, one per warehouse. ``line_errors`` is only
    populated when the request set ``reject_line_errors=False``.
    """

    orders: list[Order] = Field(
        validation_alias=AliasChoices("orders", "Orders"),
        serialization_alias="orders",
        description="The orders that were placed.",
    )
    line_errors: list[JsonValue] = Field(
        default_factory=list,
        validation_alias=AliasChoices("lineErrors", "LineErrors"),
        serialization_alias="lineErrors",
        description="Lines that could not be filled. The shape is not documented by S&S.",
    )


class PaymentProfile(SSActivewearBaseModel):
    """A saved credit card or bank account."""

    profile_id: int = Field(
        alias="profileID",
        description="Unique ID for this payment profile (used when placing orders).",
    )
    profile_type: str = Field(
        # The object definition misspells this as ``profyleType``.
        validation_alias=AliasChoices("profileType", "profyleType"),
        serialization_alias="profileType",
        description="Credit Card or Bank.",
    )
    name: str = Field(
        description="Logical name for the payment profile.",
    )
