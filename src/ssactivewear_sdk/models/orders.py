"""Order models."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field

from ._base import SSActivewearBaseModel


class OrderRequestShippingAddress(SSActivewearBaseModel):
    """Shipping address for an order."""

    customer: str = Field(
        description="Customer/Company name",
    )
    attention_to: str = Field(
        alias="attn",
        description="Attention to (recipient name)",
    )
    address: str = Field(
        description="Street address",
    )
    city: str = Field(
        description="City",
    )
    state: str = Field(
        description="State abbreviation",
    )
    postal_code: str = Field(
        alias="zip",
        description="ZIP/Postal code",
    )
    residential: bool = Field(
        default=True,
        description="Whether this is a residential address",
    )


class OrderRequestPaymentProfile(SSActivewearBaseModel):
    """Payment profile information.

    This is used of you would like to pay via a saved credit card or bank account
    on your www.ssactivewear.com website account.
    """

    email: EmailStr = Field(
        description="Email of the website user where the card is saved",
    )
    profile_id: int = Field(
        alias="profileID",
        description="ProfileID retuned in GET - /V2/paymentprofile api call for the given profile",
    )


class OrderRequestOrderLine(SSActivewearBaseModel):
    """Order line item."""

    identifier: str = Field(
        description="SkuID_Master, Sku, Gtin",
    )
    quantity: int = Field(
        alias="qty",
        description="Quantity to order",
    )
    warehouse_abbreviation: str | None = Field(
        default=None,
        alias="warehouseAbbr",
        description="Determines what warehouse to ship from.",
    )


class OrderRequest(SSActivewearBaseModel):
    """Order creation request."""

    shipping_address: OrderRequestShippingAddress = Field(
        alias="shippingAddress",
        description="Shipping address information",
    )
    lines: list[OrderRequestOrderLine] = Field(
        description="List of products to order",
    )
    shipping_method: Literal[
        "1",  # Ground (Carrier determined by S&S)
        "2",  # UPS Next Day Air
        "3",  # UPS 2nd Day Air
        "6",  # Will Call / PickUp
        "8",  # Messenger Pickup / PickUp
        "14",  # FedEx Ground
        "16",  # UPS 3 Day Select
        "17",  # UPS Next Day Air Early AM
        "19",  # UPS Saturday
        "20",  # UPS Saturday Early
        "21",  # UPS Next Day Air Saver
        "22",  # UPS 2nd Day Air AM
        "26",  # FedEx Next Day Priority
        "27",  # FedEx Next Day Standard
        "40",  # UPS Ground
        "48",  # FedEx 2nd Day Air
        "54",  # Misc Cheapest
    ] = Field(
        default="1",
        alias="shippingMethod",
        description=(
            "Shipping method: 1=Ground (Carrier determined by S&S), 2=UPS Next Day Air, "
            "3=UPS 2nd Day Air, 16=UPS 3 Day Select, 6=Will Call/PickUp, "
            "8=Messenger Pickup/PickUp, 54=Misc Cheapest, 17=UPS Next Day Air Early AM, "
            "21=UPS Next Day Air Saver, 19=UPS Saturday, 20=UPS Saturday Early, "
            "22=UPS 2nd Day Air AM, 14=FedEx Ground, 27=FedEx Next Day Standard, "
            "26=FedEx Next Day Priority, 40=UPS Ground, 48=FedEx 2nd Day Air"
        ),
    )
    ship_blind: bool | None = Field(
        default=None,
        alias="shipBlind",
        description="Override customer settings for blind shipping",
    )
    po_number: str = Field(
        default="",
        alias="poNumber",
        description="Customer PO number",
    )
    email_confirmation: str = Field(
        default="",
        alias="emailConfirmation",
        description="Email address to receive confirmation",
    )
    test_order: bool = Field(
        default=False,
        alias="testOrder",
        description="Test orders will be created and cancelled",
    )
    autoselect_warehouse: bool = Field(
        default=False,
        alias="autoselectWarehouse",
        description="Allow S&S to choose warehouse, may split between multiple warehouses",
    )
    promotion_code: str | None = Field(
        default=None,
        alias="promotionCode",
        description="Promotion code for products on the order",
    )
    autoselect_warehouse_warehouses: str | None = Field(
        default=None,
        alias="autoselectWarehouse_Warehouses",
        description=(
            "Comma-separated list of warehouse abbreviations to restrict autoselect to, "
            "e.g. 'IL,KS,GA,NV,TX,FL,OH,PA,DS,CC,CN,FO,GD,KC,MA,PH,TD'"
        ),
    )
    autoselect_warehouse_preference: Literal["fewest", "fastest"] = Field(
        default="fewest",
        alias="AutoSelectWarehouse_Preference",
        description="Freight optimizer selection: 'fewest' or 'fastest'",
    )
    autoselect_warehouse_fewest_max_dit: int = Field(
        default=10,
        alias="AutoSelectWarehouse_Fewest_MaxDIT",
        description="Maximum days in transit for 'fewest' before switching to 'fastest'",
    )
    reject_line_errors: bool = Field(
        default=True,
        alias="rejectLineErrors",
        description=(
            "If false, place order for items that can be filled; response includes both Orders and LineErrors"
        ),
    )
    reject_line_errors_email: bool = Field(
        default=True,
        alias="rejectLineErrors_Email",
        description="Email unfillable line items to emailConfirmation address",
    )
    payment_profile: OrderRequestPaymentProfile | None = Field(
        default=None,
        alias="paymentProfile",
        description="Payment profile for saved credit card or bank account",
    )


class OrderResponseShippingAddress(SSActivewearBaseModel):
    """Shipping address in order response."""

    customer: str = Field(
        description="Customer/Company name",
    )
    attn: str = Field(
        description="Attention to (recipient name)",
    )
    address: str = Field(
        description="Street address",
    )
    city: str = Field(
        description="City",
    )
    state: str = Field(
        description="State abbreviation",
    )
    zip: str = Field(
        description="ZIP/Postal code",
    )


class OrderResponseLine(SSActivewearBaseModel):
    """Order line item in response."""

    line_number: int = Field(
        alias="lineNumber",
        description="Line number in the order",
    )
    type: str = Field(
        description="Type of line item",
    )
    sku_id: int = Field(
        alias="skuID",
        description="Unique SKU ID",
    )
    sku: str = Field(
        description="SKU number",
    )
    gtin: str = Field(
        description="Global Trade Item Number",
    )
    your_sku: str = Field(
        alias="yourSku",
        description="Your custom SKU reference",
    )
    qty_ordered: int = Field(
        alias="qtyOrdered",
        description="Quantity ordered",
    )
    price: float = Field(
        description="Price per unit",
    )
    brand_name: str = Field(
        alias="brandName",
        description="Brand name",
    )
    style_name: str = Field(
        alias="styleName",
        description="Style name",
    )
    title: str = Field(
        description="Product title",
    )
    color_name: str = Field(
        alias="colorName",
        description="Color name",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size name",
    )
    returnable: bool = Field(
        description="Whether the product is eligible for return",
    )


class OrderResponse(SSActivewearBaseModel):
    """Order response."""

    guid: UUID = Field(
        description="Unique order GUID",
        strict=False,
    )
    company_name: str = Field(
        alias="companyName",
        description="Company name",
    )
    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Warehouse abbreviation",
    )
    order_number: str = Field(
        alias="orderNumber",
        description="Order number",
    )
    invoice_number: str = Field(
        alias="invoiceNumber",
        description="Invoice number",
    )
    po_number: str = Field(
        alias="poNumber",
        description="Purchase order number",
    )
    customer_number: str = Field(
        alias="customerNumber",
        description="Customer number",
    )
    order_date: datetime = Field(
        alias="orderDate",
        description="Order date",
        strict=False,
    )
    expected_delivery_date: date = Field(
        alias="expectedDeliveryDate",
        description="Expected delivery date",
        strict=False,
    )
    order_type: str = Field(
        alias="orderType",
        description="Order type (e.g., 'API')",
    )
    terms: str = Field(
        description="Payment terms",
    )
    order_status: str = Field(
        alias="orderStatus",
        description="Order status (e.g., 'In Progress')",
    )
    dropship: bool = Field(
        description="Whether this is a dropship order",
    )
    shipping_carrier: str = Field(
        alias="shippingCarrier",
        description="Shipping carrier (e.g., 'UPS')",
    )
    shipping_method: str = Field(
        alias="shippingMethod",
        description="Shipping method (e.g., 'UPS Ground')",
    )
    ship_blind: bool = Field(
        alias="shipBlind",
        description="Whether this is a blind shipment",
    )
    shipping_collect_number: str = Field(
        alias="shippingCollectNumber",
        description="Shipping collect number",
    )
    shipping_address: OrderResponseShippingAddress = Field(
        alias="shippingAddress",
        description="Shipping address",
    )
    subtotal: float = Field(
        description="Order subtotal",
    )
    shipping: float = Field(
        description="Shipping cost",
    )
    cod: float = Field(
        description="Cash on delivery fee",
    )
    tax: float = Field(
        description="Tax amount",
    )
    small_order_fee: float = Field(
        alias="smallOrderFee",
        description="Small order fee",
    )
    cupon_discount: float = Field(
        alias="cuponDiscount",
        description="Coupon discount amount",
    )
    sample_discount: float = Field(
        alias="sampleDiscount",
        description="Sample discount amount",
    )
    set_up_fee: float = Field(
        alias="setUpFee",
        description="Setup fee",
    )
    restock_fee: float = Field(
        alias="restockFee",
        description="Restock fee",
    )
    debit_credit: float = Field(
        alias="debitCredit",
        description="Debit/Credit amount",
    )
    total: float = Field(
        description="Total order amount",
    )
    total_pieces: int = Field(
        alias="totalPieces",
        description="Total number of pieces",
    )
    total_lines: int = Field(
        alias="totalLines",
        description="Total number of line items",
    )
    total_weight: float = Field(
        alias="totalWeight",
        description="Total weight in pounds",
    )
    total_boxes: int = Field(
        alias="totalBoxes",
        description="Total number of boxes",
    )
    delivery_status: str = Field(
        alias="deliveryStatus",
        description="Delivery status",
    )
    conveyor_lane: str = Field(
        alias="conveyorLane",
        description="Conveyor lane",
    )
    lines: list[OrderResponseLine] = Field(
        description="List of order line items",
    )
    shipping_saved: float = Field(
        alias="shippingSaved",
        description="Total shipping saved",
    )


class OrderResponseContainer(SSActivewearBaseModel):
    """Order response container."""

    line_errors: list[str] = Field(
        alias="lineErrors",
        description="List of line errors",
    )

    orders: list[OrderResponse] = Field(
        description="List of orders",
    )
