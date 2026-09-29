"""Testing the models against S&S' documented examples."""

import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import TypeAdapter, ValidationError

from ssactivewear_sdk import (
    Brand,
    Category,
    CrossReference,
    DaysInTransit,
    ErrorResponse,
    InventoryItem,
    Order,
    OrderLineRequest,
    OrderRequest,
    OrderShippingAddress,
    PaymentProfile,
    PaymentProfileReference,
    Product,
    ReturnOrder,
    ReturnReason,
    ReturnRequest,
    ReturnRequestLine,
    ShippingMethod,
    Spec,
    Style,
    TrackingData,
)

from .helpers import example

# ---------------------------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------------------------


def test_categories_example_parses() -> None:
    """The documented category parses."""
    (category,) = TypeAdapter(list[Category]).validate_json(example("categories.json"))

    assert category.category_id == 81  # noqa: PLR2004
    assert category.name == "3/4 Sleeve"
    assert category.image == "deprecated"


def test_brands_example_parses() -> None:
    """The documented brand parses."""
    (brand,) = TypeAdapter(list[Brand]).validate_json(example("brands.json"))

    assert brand.brand_id == 31  # noqa: PLR2004
    assert brand.name == "Adidas"
    assert brand.no_eretailing is True


def test_styles_example_parses() -> None:
    """The documented style parses, including its ``assetType`` media assets."""
    (style,) = TypeAdapter(list[Style]).validate_json(example("styles.json"))

    assert style.style_id == 39  # noqa: PLR2004
    assert style.base_category == "T-Shirts"
    assert style.category_ids == [21, 57, 71, 79, 87]
    assert style.comparable_group == 7  # noqa: PLR2004
    assert style.companion_group == 2  # noqa: PLR2004
    assert style.sustainable_style is True
    assert [(asset.image, asset.asset_type) for asset in style.media_assets] == [("Images/Style/39_fm.jpg", "Style")]


def test_style_accepts_the_object_definition_spellings() -> None:
    """The object definition's ``baseCateogry``, string groups, and ``asset_type`` are accepted too."""
    payload = json.loads(example("styles.json"))[0]
    payload["baseCateogry"] = payload.pop("baseCategory")
    payload["comparableGroup"] = "7"
    payload["companionGroup"] = ""
    payload["mediaAssets"] = [{"image": "Images/Style/39_fm.jpg", "asset_type": "Style"}]

    style = Style.model_validate_json(json.dumps(payload))

    assert style.base_category == "T-Shirts"
    assert style.comparable_group == 7  # noqa: PLR2004
    assert style.companion_group is None
    assert style.media_assets[0].asset_type == "Style"


def test_products_example_parses() -> None:
    """The documented product parses, with prices as decimals and every warehouse."""
    (product,) = TypeAdapter(list[Product]).validate_json(example("products.json"))

    assert product.sku == "B00760004"
    assert product.sku_id_master == 2343  # noqa: PLR2004
    assert product.brand_id == "35"
    assert product.color_family_id == "19"
    assert product.base_category_id == "16"
    assert product.unit_weight == Decimal("0.4208")
    assert product.retail_price == Decimal("6.90")
    assert product.customer_price == Decimal("2.72")
    assert product.sale_expiration == datetime(2026, 7, 30)  # noqa: DTZ001
    assert product.poly_pack_qty == 0
    assert [warehouse.warehouse_abbr for warehouse in product.warehouses] == [
        "KS",
        "DS",
        "TX",
        "GA",
        "NV",
        "IL",
        "OH",
        "PA",
        "CN",
        "FO",
        "MA",
    ]
    assert product.warehouses[1].dropship is True
    assert product.warehouses[3].expected_inventory == "EnRoute:None|OnOrder:2026-1000+, "
    assert [asset.asset_type for asset in product.media_assets] == [
        "Style",
        "Front",
        "Back",
        "DirectSide",
        "OnModel_Front",
        "OnModel_Back",
        "OnModel_Side",
    ]


def test_product_accepts_the_object_definition_shapes() -> None:
    """Integer IDs, ``PolyPackQty``, and ``MM/DD/YYYY`` sale expirations are accepted too."""
    payload = json.loads(example("products.json"))[0]
    payload["brandID"] = 35
    payload["colorFamilyID"] = 19
    payload["PolyPackQty"] = payload.pop("polyPackQty")
    payload["saleExpiration"] = "07/30/2026"
    del payload["retailPrice"]

    product = Product.model_validate_json(json.dumps(payload))

    assert product.brand_id == "35"
    assert product.color_family_id == "19"
    assert product.poly_pack_qty == 0
    assert product.sale_expiration == datetime(2026, 7, 30)  # noqa: DTZ001
    assert product.retail_price is None


@pytest.mark.parametrize("sale_expiration", ["", None])
def test_product_without_a_sale_has_no_expiration(sale_expiration: str | None) -> None:
    """An empty or null sale expiration is treated as no sale."""
    payload = json.loads(example("products.json"))[0]
    payload["saleExpiration"] = sale_expiration

    assert Product.model_validate_json(json.dumps(payload)).sale_expiration is None


def test_product_ignores_fields_it_does_not_know() -> None:
    """A field S&S adds later does not break parsing."""
    payload = json.loads(example("products.json"))[0]
    payload["someNewField"] = {"nested": True}

    assert Product.model_validate_json(json.dumps(payload)).sku == "B00760004"


def test_inventory_example_parses() -> None:
    """The documented inventory item parses."""
    (item,) = TypeAdapter(list[InventoryItem]).validate_json(example("inventory.json"))

    assert item.sku_id_master == 2343  # noqa: PLR2004
    assert [(warehouse.warehouse_abbr, warehouse.qty) for warehouse in item.warehouses] == [
        ("IL", 10000),
        ("NV", 0),
        ("NJ", 2210),
        ("KS", 7326),
    ]


def test_inventory_accepts_the_object_definition_sku_id() -> None:
    """The object definition calls the master sku ID ``skuID``."""
    payload = json.loads(example("inventory.json"))[0]
    payload["skuID"] = payload.pop("skuID_Master")

    assert InventoryItem.model_validate_json(json.dumps(payload)).sku_id_master == 2343  # noqa: PLR2004


def test_specs_example_parses() -> None:
    """The documented spec parses."""
    (spec,) = TypeAdapter(list[Spec]).validate_json(example("specs.json"))

    assert (spec.spec_id, spec.style_id, spec.spec_name, spec.value) == (39, 253, "Neck Size", "16")


# ---------------------------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------------------------


def test_orders_example_parses() -> None:
    """The documented order parses, with the fields only sent once it has shipped."""
    (order,) = TypeAdapter(list[Order]).validate_json(example("orders.json"))

    assert order.guid == UUID("e66b7667-868f-4ae0-b605-2f45fbd288c0")
    assert order.order_number == "4629304"
    assert order.order_date == datetime(2014, 6, 18, 10, 59, 6, 430000)  # noqa: DTZ001
    assert order.ship_date == datetime(2014, 6, 18, 14, 15, 31, 613000)  # noqa: DTZ001
    assert order.invoice_date == datetime(2014, 6, 18)  # noqa: DTZ001
    assert order.tracking_number == "1ZE9W0610315091599"
    assert order.shipping_address.zip == "54754"
    assert order.lost_cash_discount == Decimal("0.00")
    assert order.total == Decimal("144.38")
    assert order.total_boxes == 1
    assert order.lines == []
    assert order.billing_address is None


def test_placed_order_example_parses() -> None:
    """The documented order placement response parses."""
    (order,) = TypeAdapter(list[Order]).validate_json(example("orders_create.json"))

    assert order.order_status == "In Progress"
    assert order.expected_delivery_date == datetime(2021, 9, 29)  # noqa: DTZ001
    assert order.conveyor_lane == "8"
    assert order.ship_date is None
    (line,) = order.lines
    assert (line.sku, line.qty_ordered, line.price, line.returnable) == ("B22060655", 12, Decimal("3.22"), True)


def test_cancelled_order_example_parses() -> None:
    """The documented cancellation response parses without the fields it leaves out."""
    (order,) = TypeAdapter(list[Order]).validate_json(example("orders_cancel.json"))

    assert order.order_status == "Cancelled"
    assert order.shipping_saved is None
    assert order.delivery_status is None


def test_order_billing_address_and_boxes_parse() -> None:
    """The billing address and boxes, sent on request, parse."""
    payload = json.loads(example("orders.json"))[0]
    payload["billingAddress"] = {
        "billTo": "Timesaver",
        "attn": "Accounts Payable",
        "address": "W8020 W Clay School Rd",
        "city": "Merrillan",
        "state": "WI",
        "zip": "54754",
    }
    payload["boxes"] = [
        {
            "boxNumber": 1,
            "trackingNumber": "1ZE9W0610315091599",
            "weight": 17.35,
            "cubicVolume": 1.5,
            "conveyorBarcode": "907070.0011",
            "lines": [],
        }
    ]

    order = Order.model_validate_json(json.dumps(payload))

    assert order.billing_address is not None
    assert order.billing_address.bill_to == "Timesaver"
    assert order.boxes[0].weight == Decimal("17.35")
    assert order.boxes[0].return_information is None


def test_payment_profiles_example_parses() -> None:
    """The documented payment profile parses, including its extra level of nesting."""
    ((profile,),) = TypeAdapter(list[list[PaymentProfile]]).validate_json(example("payment_profiles.json"))

    assert (profile.profile_id, profile.profile_type, profile.name) == (
        123456789,
        "Credit Card",
        "BMO Harris Bank 1234 (John Doe)",
    )


def test_payment_profile_accepts_the_object_definition_spelling() -> None:
    """The object definition misspells ``profileType`` as ``profyleType``."""
    profile = PaymentProfile.model_validate_json(b'{"profileID": 1, "profyleType": "Bank", "name": "Checking"}')

    assert profile.profile_type == "Bank"


def test_order_request_matches_the_documented_example() -> None:
    """An order request serializes to the documented request body."""
    order = OrderRequest(
        shipping_address=OrderShippingAddress(
            customer="Company ABC",
            attn="John Doe",
            address="123 Main St",
            city="Bolingbrook",
            state="IL",
            zip="60440",
            residential=True,
        ),
        shipping_method=ShippingMethod.GROUND,
        ship_blind=False,
        po_number="Test",
        email_confirmation="",
        test_order=False,
        autoselect_warehouse=True,
        lines=[OrderLineRequest(identifier="B00760003", qty=2)],
    )

    assert order.model_dump(mode="json", by_alias=True, exclude_none=True) == json.loads(
        example("orders_create_request.json")
    )


def test_order_request_serializes_every_option() -> None:
    """Warehouse lists are comma joined, the ship by date is ``MM/DD/YYYY``, and names are S&S'."""
    order = OrderRequest(
        shipping_address=OrderShippingAddress(address="123 Main St", city="Bolingbrook", state="IL", zip="60440"),
        lines=[OrderLineRequest(identifier="B00760003", qty=2, warehouse_abbr="IL")],
        shipping_method=ShippingMethod.MISC_CHEAPEST,
        promotion_code="SPRING",
        autoselect_warehouse=True,
        autoselect_warehouse_warehouses=["IL", "KS", "GA"],
        autoselect_warehouse_preference="fastest",
        autoselect_warehouse_fewest_max_dit=3,
        reject_line_errors=False,
        reject_line_errors_email=False,
        payment_profile=PaymentProfileReference(email="buyer@example.com", profile_id=123456789),
        ship_by_date=date(2026, 10, 2),
    )

    assert order.model_dump(mode="json", by_alias=True, exclude_none=True) == {
        "shippingAddress": {"address": "123 Main St", "city": "Bolingbrook", "state": "IL", "zip": "60440"},
        "lines": [{"identifier": "B00760003", "qty": 2, "warehouseAbbr": "IL"}],
        "shippingMethod": "54",
        "promotionCode": "SPRING",
        "autoselectWarehouse": True,
        "autoselectWarehouse_Warehouses": "IL,KS,GA",
        "AutoSelectWarehouse_Preference": "fastest",
        "AutoSelectWarehouse_Fewest_MaxDIT": 3,
        "rejectLineErrors": False,
        "rejectLineErrors_Email": False,
        "paymentProfile": {"email": "buyer@example.com", "profileID": 123456789},
        "shipByDate": "10/02/2026",
    }


# ---------------------------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------------------------


def test_returns_example_parses() -> None:
    """The documented credit and replacement orders parse."""
    credit, replacement = TypeAdapter(list[ReturnOrder]).validate_json(example("returns.json"))

    assert credit.order_type == "Credit"
    assert credit.total_pieces == -20  # noqa: PLR2004
    assert credit.lines[0].qty_ordered == -20  # noqa: PLR2004
    assert credit.return_information is not None
    assert credit.return_information.return_items_required is True
    assert credit.return_information.return_to_address is not None
    assert credit.return_information.return_to_address.city == "Fort Worth"
    assert credit.return_information.original_invoices == ["400000"]
    (box,) = credit.boxes
    assert box.box_required is False
    assert box.return_information is not None
    assert box.return_information.shipping_label_zpl == "XXXXXXX"
    assert box.lines[0].price is None

    assert replacement.order_type == "Replacement"
    assert replacement.return_information is not None
    assert replacement.return_information.shipping_label_url is None
    assert replacement.return_information.return_reason == "Wrong style or color"


def test_return_information_splits_several_original_invoices() -> None:
    """Several original invoices arrive comma separated."""
    payload = json.loads(example("returns.json"))[0]
    payload["returnInformation"]["originalInvoice"] = "3000000,4000000, 5000000"

    order = ReturnOrder.model_validate_json(json.dumps(payload))

    assert order.return_information is not None
    assert order.return_information.original_invoices == ["3000000", "4000000", "5000000"]


@pytest.mark.parametrize("name", ["returns_create.json", "returns_cancel.json"])
def test_other_return_examples_parse(name: str) -> None:
    """The documented return creation and cancellation responses parse."""
    assert TypeAdapter(list[ReturnOrder]).validate_json(example(name))


def test_return_request_serializes_with_the_documented_names() -> None:
    """A return request uses the object definition's names and types.

    The published example is not valid JSON (``"invoiceNumber": 0000000``) and disagrees with
    the object definition on ``Qty`` and the type of ``returnReason``; the definition wins.
    """
    request = ReturnRequest(
        email_confirmation="returns@example.com",
        shipping_label_required=True,
        test_order=False,
        lines=[
            ReturnRequestLine(
                invoice_number="0000000",
                identifier="K22035134",
                qty=2,
                return_reason=ReturnReason.DAMAGED_OR_DEFECTIVE,
                is_replace=True,
                return_reason_comment="some comment",
            )
        ],
    )

    assert request.model_dump(mode="json", by_alias=True, exclude_none=True) == {
        "emailConfirmation": "returns@example.com",
        "shippingLabelRequired": True,
        "testOrder": False,
        "lines": [
            {
                "invoiceNumber": "0000000",
                "identifier": "K22035134",
                "qty": 2,
                "returnReason": "2",
                "isReplace": True,
                "returnReasonComment": "some comment",
            }
        ],
    }


@pytest.mark.parametrize("reason", [ReturnReason.DAMAGED_OR_DEFECTIVE, ReturnReason.OTHER])
@pytest.mark.parametrize("comment", [None, " "])
def test_replacement_for_some_reasons_needs_a_comment(reason: ReturnReason, comment: str | None) -> None:
    """S&S requires a comment to replace a damaged item or one returned for another reason."""
    with pytest.raises(ValidationError, match="return_reason_comment"):
        ReturnRequestLine(
            invoice_number="1",
            identifier="K22035134",
            qty=1,
            return_reason=reason,
            is_replace=True,
            return_reason_comment=comment,
        )


@pytest.mark.parametrize(
    ("reason", "is_replace"),
    [
        (ReturnReason.DAMAGED_OR_DEFECTIVE, False),
        (ReturnReason.OTHER, None),
        (ReturnReason.DO_NOT_NEED, True),
    ],
)
def test_other_returns_do_not_need_a_comment(reason: ReturnReason, *, is_replace: bool | None) -> None:
    """Only replacements for reasons 2 and 6 need a comment."""
    line = ReturnRequestLine(
        invoice_number="1", identifier="K22035134", qty=1, return_reason=reason, is_replace=is_replace
    )

    assert line.return_reason_comment is None


# ---------------------------------------------------------------------------------------------
# Cross references and shipping
# ---------------------------------------------------------------------------------------------


def test_cross_references_example_parses() -> None:
    """The documented cross reference parses."""
    (cross_reference,) = TypeAdapter(list[CrossReference]).validate_json(example("cross_references.json"))

    assert (cross_reference.your_sku, cross_reference.sku_id, cross_reference.sku) == ("G2000whtxl", 2345, "B00760003")


def test_days_in_transit_example_parses() -> None:
    """The documented days in transit parse."""
    (transit,) = TypeAdapter(list[DaysInTransit]).validate_json(example("days_in_transit.json"))

    assert transit.zip_code == "60440"
    assert [(warehouse.warehouse_abbr, warehouse.days_in_transit) for warehouse in transit.warehouses] == [
        ("IL", 1),
        ("NJ", 3),
        ("KS", 2),
        ("NV", 4),
    ]
    assert transit.warehouses[0].cut_off_time_24hr == "16:00"


def test_tracking_example_parses() -> None:
    """The documented tracking data parses."""
    ((tracking,),) = TypeAdapter(list[list[TrackingData]]).validate_json(example("tracking.json"))

    assert tracking.carrier_name == "USPS"
    assert tracking.actual_delivery_date_time == datetime(2021, 5, 10, 16, 11)  # noqa: DTZ001
    assert tracking.latest_checkpoint is not None
    assert tracking.latest_checkpoint.checkpoint_location == "MARSING, ID, US"
    assert tracking.order_number == "32526736"
    assert tracking.box_number is None


def test_tracking_before_delivery_parses() -> None:
    """A shipment that has not been delivered yet has no delivery time."""
    tracking = TrackingData.model_validate_json(
        b'{"trackingNumber": "1Z", "actualDeliveryDateTime": "", "boxNumber": 2}'
    )

    assert tracking.actual_delivery_date_time is None
    assert tracking.box_number == 2  # noqa: PLR2004


# ---------------------------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------------------------


def test_bad_request_example_parses() -> None:
    """The documented 400 body parses and describes each problem."""
    error = ErrorResponse.model_validate_json(example("error_400.json"))

    assert error.code == "400"
    assert error.describe() == (
        "Bad Request. Header: You must set the Content-Type header when doing this request.  "
        "Options are application/json or application/xml."
    )


@pytest.mark.parametrize(
    ("name", "description"),
    [
        ("error_404_not_found.json", "Identifier: Requested item(s) were not found or have been discontinued."),
        (
            "error_404_route.json",
            (
                "No HTTP resource was found that matches the request URI "
                "'https://apidev.ssactivewear.com/V1/orderss'. "
                "No type was found that matches the controller named 'orders'."
            ),
        ),
        ("error_500.json", "An unhandled exception was thrown by Customer Web API controller."),
    ],
)
def test_other_error_examples_parse(name: str, description: str) -> None:
    """Every documented error body parses, whichever fields it leaves out."""
    assert ErrorResponse.model_validate_json(example(name)).describe() == description


def test_empty_error_has_no_description() -> None:
    """An error body without any detail describes nothing."""
    assert ErrorResponse.model_validate_json(b"{}").describe() is None


def test_unparseable_sale_expiration_is_rejected() -> None:
    """A timestamp in neither documented format fails validation instead of being guessed at."""
    payload = json.loads(example("products.json"))[0]
    payload["saleExpiration"] = "next Tuesday"

    with pytest.raises(ValidationError, match="saleExpiration"):
        Product.model_validate_json(json.dumps(payload))


def test_order_request_unset_options_serialize_as_null() -> None:
    """Without ``exclude_none``, unset list and date options stay null rather than being formatted."""
    order = OrderRequest(
        shipping_address=OrderShippingAddress(address="123 Main St", city="Bolingbrook", state="IL", zip="60440"),
        lines=[OrderLineRequest(identifier="B00760003", qty=2)],
    )

    dumped = order.model_dump(mode="json", by_alias=True)

    assert dumped["autoselectWarehouse_Warehouses"] is None
    assert dumped["shipByDate"] is None
