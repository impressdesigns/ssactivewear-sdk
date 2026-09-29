"""Testing the client."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

import pytest

from ssactivewear_sdk import (
    InvoicePDF,
    OrderLineRequest,
    OrderRequest,
    OrderShippingAddress,
    ReturnReason,
    ReturnRequest,
    ReturnRequestLine,
    SSActivewear,
    SSActivewearAPIError,
    SSActivewearBadRequestError,
    SSActivewearNotFoundError,
)

from .helpers import example

ACCOUNT_NUMBER = "12345"
API_KEY = "0f8fad5b-d9cb-469f-a165-70867728950e"


@dataclass
class FakeResponse:
    """Stand in for a niquests response."""

    content: bytes = b"[]"
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Mirror niquests: anything below 400 is fine."""
        return self.status_code < 400  # noqa: PLR2004


def _build_client() -> SSActivewear:
    """Build a client with placeholder credentials."""
    return SSActivewear(ACCOUNT_NUMBER, API_KEY)


def _stub_session(
    client: SSActivewear,
    monkeypatch: pytest.MonkeyPatch,
    *responses: FakeResponse,
) -> list[dict[str, object]]:
    """Answer requests in memory, in order, recording what was sent."""
    sent: list[dict[str, object]] = []
    queue = list(responses)

    def request(**kwargs: object) -> FakeResponse:
        sent.append(kwargs)
        return queue.pop(0)

    monkeypatch.setattr(client.client, "request", request)
    return sent


def _refuse_requests(client: SSActivewear, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if a request is sent."""
    monkeypatch.setattr(
        client.client,
        "request",
        lambda **_kwargs: pytest.fail("Invalid input must not send a request."),
    )


# ---------------------------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------------------------


def test_client_authenticates_with_account_number_and_api_key() -> None:
    """The account number and API key are the basic auth credentials."""
    client = _build_client()

    assert client.client.auth == (ACCOUNT_NUMBER, API_KEY)
    assert client.client.base_url == "https://api.ssactivewear.com/v2"


@pytest.mark.parametrize(
    ("account_number", "api_key", "expected_message"),
    [
        ("", API_KEY, "account_number"),
        ("12a45", API_KEY, "account_number"),
        (ACCOUNT_NUMBER, "", "api_key"),
        (ACCOUNT_NUMBER, "not-a-uuid", "api_key"),
    ],
)
def test_client_rejects_invalid_credentials(account_number: str, api_key: str, expected_message: str) -> None:
    """Credentials that cannot be valid are rejected before any request."""
    with pytest.raises(ValueError, match=expected_message):
        SSActivewear(account_number, api_key)


# ---------------------------------------------------------------------------------------------
# GET requests
# ---------------------------------------------------------------------------------------------


type Call = Callable[[SSActivewear], list[object]]

GET_REQUESTS: list[tuple[Call, str, str]] = [
    # Catalog
    (lambda client: list(client.get_categories()), "categories.json", "/categories/"),
    (lambda client: list(client.get_categories([81, 82])), "categories.json", "/categories/81,82"),
    (lambda client: list(client.get_brands(31)), "brands.json", "/Brands/31"),
    (lambda client: list(client.get_styles()), "styles.json", "/styles/"),
    (lambda client: list(client.get_styles(["00760", "Gildan 5000"])), "styles.json", "/styles/00760,Gildan%205000"),
    (lambda client: list(client.get_styles(search="Gildan 2000")), "styles.json", "/styles/?search=Gildan%202000"),
    (
        lambda client: list(client.get_styles(style_ids=[39, 40], part_numbers="00760")),
        "styles.json",
        "/styles/?styleid=39,40&partnumber=00760",
    ),
    (lambda client: list(client.get_products()), "products.json", "/products/"),
    (
        lambda client: list(client.get_products([81480, "B00760004", "00821780008137"])),
        "products.json",
        "/products/81480,B00760004,00821780008137",
    ),
    (
        lambda client: list(client.get_products(styles=["00760", "Gildan 5000"])),
        "products.json",
        "/products/?style=00760,Gildan%205000",
    ),
    (
        lambda client: list(client.get_products(styles="bella + canvas 3001cvc")),
        "products.json",
        "/products/?style=bella%20%2B%20canvas%203001cvc",
    ),
    (
        lambda client: list(client.get_products("B00760003", warehouses=["IL", "KS"])),
        "products.json",
        "/products/B00760003?Warehouses=IL,KS",
    ),
    (
        lambda client: list(client.get_products(style_ids=39, part_numbers="00760")),
        "products.json",
        "/products/?styleid=39&partnumber=00760",
    ),
    (lambda client: list(client.get_inventory("B00760004")), "inventory.json", "/inventory/B00760004"),
    (
        lambda client: list(client.get_inventory(styles="00760", warehouses="IL")),
        "inventory.json",
        "/inventory/?style=00760&Warehouses=IL",
    ),
    (
        lambda client: list(client.get_inventory(style_ids=[39], part_numbers=["00760"])),
        "inventory.json",
        "/inventory/?styleid=39&partnumber=00760",
    ),
    (lambda client: list(client.get_specs(634)), "specs.json", "/specs/634"),
    (lambda client: list(client.get_specs(styles=[39, "Gildan 5000"])), "specs.json", "/specs/?style=39,Gildan%205000"),
    # Orders
    (lambda client: list(client.get_orders()), "orders.json", "/orders/"),
    (lambda client: list(client.get_orders(["PO", 123456])), "orders.json", "/orders/PO,123456"),
    (lambda client: list(client.get_orders(include_invoiced=True)), "orders.json", "/orders/?All=true"),
    (
        lambda client: list(client.get_orders(invoice_dates=[date(2014, 6, 18), date(2014, 6, 19)])),
        "orders.json",
        "/orders/?invoicedate=2014-06-18,2014-06-19",
    ),
    (
        lambda client: list(client.get_orders(invoice_date_range=(date(2014, 6, 18), date(2015, 6, 19)))),
        "orders.json",
        "/orders/?invoicestartdate=2014-06-18&invoiceenddate=2015-06-19",
    ),
    (
        lambda client: list(client.get_orders(shipping_label_barcode="57926652.0031", sort_by="packing")),
        "orders.json",
        "/orders/?shippinglabelbarcode=57926652.0031&sortby=packing",
    ),
    (
        lambda client: list(
            client.get_orders(
                lines=True,
                boxes=True,
                billing=True,
                include_ar_child_invoices=True,
                sort_by="linenumber",
            )
        ),
        "orders.json",
        "/orders/?lines=true&Boxes=true&Billing=true&includeARChildInvoices=true&sortby=linenumber",
    ),
    (
        lambda client: list(client.get_payment_profiles("test@abc.com")),
        "payment_profiles.json",
        "/paymentprofiles/?email=test%40abc.com",
    ),
    # Returns
    (lambda client: list(client.get_returns()), "returns.json", "/returns/"),
    (lambda client: list(client.get_returns(4629304)), "returns.json", "/returns/4629304"),
    (
        lambda client: list(client.get_returns(invoice_dates=date(2014, 6, 18), lines=True, boxes=True)),
        "returns.json",
        "/returns/?invoicedate=2014-06-18&lines=true&Boxes=true",
    ),
    # Cross references
    (lambda client: list(client.get_cross_references()), "cross_references.json", "/crossref/"),
    (lambda client: list(client.get_cross_references("G2000whtxl")), "cross_references.json", "/crossref/G2000whtxl"),
    # Shipping
    (lambda client: list(client.get_days_in_transit()), "days_in_transit.json", "/daysintransit/"),
    (lambda client: list(client.get_days_in_transit(60440)), "days_in_transit.json", "/daysintransit/60440"),
    (lambda client: list(client.get_all_tracking()), "tracking.json", "/TrackingDataGetAll/"),
    (
        lambda client: list(client.get_tracking_by_invoice([43937002, 43937003], boxes=True)),
        "tracking.json",
        "/TrackingDataByInvoice/43937002,43937003?Boxes=true",
    ),
    (
        lambda client: list(client.get_tracking_by_order_number([32526736, 32526740])),
        "tracking.json",
        "/TrackingDataByOrderNum/32526736,32526740",
    ),
    (
        lambda client: list(client.get_tracking_by_tracking_number("9400111898524897753577")),
        "tracking.json",
        "/TrackingDataByTrackingNum/9400111898524897753577",
    ),
    (
        lambda client: list(client.get_tracking_by_ship_date([date(2021, 5, 7), date(2021, 5, 8)])),
        "tracking.json",
        "/TrackingDataByShipDate/2021-05-07,2021-05-08",
    ),
    (
        lambda client: list(client.get_tracking_by_ship_date_range(date(2021, 5, 1), date(2021, 5, 31))),
        "tracking.json",
        "/TrackingDataByShippingDateRange/2021-05-01,2021-05-31",
    ),
    (
        lambda client: list(client.get_tracking_by_delivery_date(date(2021, 5, 10), boxes=True)),
        "tracking.json",
        "/TrackingDataByActualDeliveryDate/2021-05-10?Boxes=true",
    ),
]


@pytest.mark.parametrize(
    ("call", "example_name", "url"),
    [pytest.param(*get_request, id=get_request[2]) for get_request in GET_REQUESTS],
)
def test_get_requests(
    monkeypatch: pytest.MonkeyPatch,
    call: Call,
    example_name: str,
    url: str,
) -> None:
    """Each GET is sent to the documented URL and returns the parsed example."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(example(example_name)))

    results = call(client)

    assert sent == [{"method": "GET", "url": url, "json": None}]
    assert results


@pytest.mark.parametrize(
    ("call", "example_name"),
    [
        (lambda client: list(client.get_payment_profiles("test@abc.com")), "payment_profiles.json"),
        (lambda client: list(client.get_all_tracking()), "tracking.json"),
    ],
)
def test_nested_lists_are_flattened(monkeypatch: pytest.MonkeyPatch, call: Call, example_name: str) -> None:
    """Payment profiles and tracking are documented as a list of lists; either shape gives a flat list."""
    nested = json.loads(example(example_name))
    flat = [item for inner in nested for item in inner]

    for payload in (nested, flat):
        client = _build_client()
        _stub_session(client, monkeypatch, FakeResponse(json.dumps(payload).encode()))

        results = call(client)

        assert len(results) == 1
        assert not isinstance(results[0], list)


# ---------------------------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------------------------


def _order_request() -> OrderRequest:
    """Build a small order."""
    return OrderRequest(
        shipping_address=OrderShippingAddress(address="123 Main St", city="Bolingbrook", state="IL", zip="60440"),
        lines=[OrderLineRequest(identifier="B00760003", qty=2)],
        reject_line_errors=False,
    )


def test_create_order_posts_the_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """An order is posted with only the fields that were set, and the placed orders are returned."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(example("orders_create.json")))

    submission = client.create_order(_order_request())

    assert sent == [
        {
            "method": "POST",
            "url": "/orders/",
            "json": {
                "shippingAddress": {"address": "123 Main St", "city": "Bolingbrook", "state": "IL", "zip": "60440"},
                "lines": [{"identifier": "B00760003", "qty": 2}],
                "rejectLineErrors": False,
            },
        }
    ]
    assert [order.order_number for order in submission.orders] == ["12345678"]
    assert submission.line_errors == []


@pytest.mark.parametrize(("orders_key", "line_errors_key"), [("orders", "lineErrors"), ("Orders", "LineErrors")])
def test_create_order_keeps_line_errors(
    monkeypatch: pytest.MonkeyPatch,
    orders_key: str,
    line_errors_key: str,
) -> None:
    """With ``reject_line_errors=False``, lines S&S could not fill come back beside the orders."""
    client = _build_client()
    line_error = {"identifier": "B00760099", "message": "Out of stock."}
    payload = {orders_key: json.loads(example("orders_create.json")), line_errors_key: [line_error]}
    _stub_session(client, monkeypatch, FakeResponse(json.dumps(payload).encode()))

    submission = client.create_order(_order_request())

    assert len(submission.orders) == 1
    assert submission.line_errors == [line_error]


def test_cancel_order_deletes_the_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cancelling sends a DELETE for the order number and returns what was cancelled."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(example("orders_cancel.json")))

    (order,) = client.cancel_order(9490497)

    assert sent == [{"method": "DELETE", "url": "/orders/9490497", "json": None}]
    assert order.order_status == "Cancelled"


# ---------------------------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("call", "url"),
    [
        (lambda client: client.get_invoice_pdf(83713072), "/Invoices/83713072"),
        (
            lambda client: client.get_invoice_pdf_by_guid(UUID("54d61c23-2b42-4021-ae34-5e6bba9eb36a")),
            "/Invoices/?Guid=54d61c23-2b42-4021-ae34-5e6bba9eb36a",
        ),
        (lambda client: client.get_invoice_pdf_by_order_number(61519822), "/Invoices/?OrderNumber=61519822"),
    ],
)
def test_invoices_are_downloaded_as_pdfs(
    monkeypatch: pytest.MonkeyPatch,
    call: Callable[[SSActivewear], object],
    url: str,
) -> None:
    """Invoices come back as PDF bytes with the file name S&S suggests."""
    client = _build_client()
    pdf = b"%PDF-1.7\n"
    sent = _stub_session(
        client,
        monkeypatch,
        FakeResponse(
            pdf,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="Lockport_Invoice_83713072.pdf"',
            },
        ),
    )

    invoice = call(client)

    assert sent == [{"method": "GET", "url": url, "json": None}]
    assert invoice == InvoicePDF(filename="Lockport_Invoice_83713072.pdf", content=pdf)


def test_invoice_without_a_file_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """A PDF without a Content-Disposition header has no file name."""
    client = _build_client()
    _stub_session(client, monkeypatch, FakeResponse(b"%PDF-1.7\n"))

    assert client.get_invoice_pdf(83713072).filename is None


# ---------------------------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------------------------


def test_create_return_posts_the_return(monkeypatch: pytest.MonkeyPatch) -> None:
    """A return is posted and the credit and replacement orders are returned."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(example("returns_create.json")))

    orders = client.create_return(
        ReturnRequest(
            lines=[
                ReturnRequestLine(
                    invoice_number="400000",
                    identifier="B86129175",
                    qty=20,
                    return_reason=ReturnReason.PICKING_ERROR_WRONG_STYLE_OR_COLOR,
                    is_replace=True,
                )
            ],
            show_boxes=True,
        )
    )

    assert sent == [
        {
            "method": "POST",
            "url": "/returns/",
            "json": {
                "lines": [
                    {
                        "invoiceNumber": "400000",
                        "identifier": "B86129175",
                        "qty": 20,
                        "returnReason": "11",
                        "isReplace": True,
                    }
                ],
                "showBoxes": True,
            },
        }
    ]
    assert [order.order_type for order in orders] == ["Credit", "Replacement"]


def test_cancel_return_deletes_the_return(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cancelling a return sends a DELETE for the order number."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(example("returns_cancel.json")))

    (order,) = client.cancel_return("9490497")

    assert sent == [{"method": "DELETE", "url": "/returns/9490497", "json": None}]
    assert order.order_status == "Cancelled"


# ---------------------------------------------------------------------------------------------
# Cross references
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(("status_code", "created"), [(201, True), (200, False)])
def test_set_cross_reference(monkeypatch: pytest.MonkeyPatch, status_code: int, *, created: bool) -> None:
    """The mapping is PUT with the identifier in the query string, and reports whether it was new."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(b"", status_code=status_code))

    assert client.set_cross_reference("G2000 wht-xl_1", "B00760003") is created
    assert sent == [{"method": "PUT", "url": "/crossref/G2000%20wht-xl_1?Identifier=B00760003", "json": None}]


def test_delete_cross_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mapping is deleted."""
    client = _build_client()
    sent = _stub_session(client, monkeypatch, FakeResponse(b"", status_code=204))

    client.delete_cross_reference("G2000whtxl")

    assert sent == [{"method": "DELETE", "url": "/crossref/G2000whtxl", "json": None}]


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda client: client.set_cross_reference("G2000/wht", "B00760003"), id="slash"),
        pytest.param(lambda client: client.set_cross_reference("", "B00760003"), id="blank"),
        pytest.param(lambda client: client.delete_cross_reference("G2000,wht"), id="comma"),
    ],
)
def test_cross_reference_rejects_invalid_skus(
    monkeypatch: pytest.MonkeyPatch,
    call: Callable[[SSActivewear], object],
) -> None:
    """Your sku may only use the characters S&S allows."""
    client = _build_client()
    _refuse_requests(client, monkeypatch)

    with pytest.raises(ValueError, match="your_sku"):
        call(client)


# ---------------------------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("call", "expected_message"),
    [
        pytest.param(lambda client: client.get_products([]), "At least one identifier", id="no-identifiers"),
        pytest.param(lambda client: client.get_products(" "), "blank", id="blank-identifier"),
        pytest.param(lambda client: client.get_products("B00760003,B00760004"), "comma", id="comma"),
        pytest.param(lambda client: client.get_products(styles=[]), "At least one identifier", id="no-styles"),
        pytest.param(lambda client: client.get_tracking_by_ship_date([]), "At least one date", id="no-dates"),
    ],
)
def test_invalid_identifiers_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    call: Callable[[SSActivewear], object],
    expected_message: str,
) -> None:
    """Identifiers that would build a wrong request fail before it is sent."""
    client = _build_client()
    _refuse_requests(client, monkeypatch)

    with pytest.raises(ValueError, match=expected_message):
        call(client)


# ---------------------------------------------------------------------------------------------
# Errors and rate limiting
# ---------------------------------------------------------------------------------------------


def test_bad_request_raises_with_the_error_details(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 400 raises with every problem S&S listed."""
    client = _build_client()
    _stub_session(client, monkeypatch, FakeResponse(example("error_400.json"), status_code=400))

    with pytest.raises(SSActivewearBadRequestError, match="Content-Type header") as excinfo:
        client.create_order(_order_request())

    assert excinfo.value.status_code == 400  # noqa: PLR2004
    assert excinfo.value.response is not None
    assert excinfo.value.response.errors[0].field == "Header"


def test_not_found_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 404 for unknown identifiers raises a not found error."""
    client = _build_client()
    _stub_session(client, monkeypatch, FakeResponse(example("error_404_not_found.json"), status_code=404))

    with pytest.raises(SSActivewearNotFoundError, match="were not found or have been discontinued") as excinfo:
        client.get_products("B99999999")

    assert excinfo.value.response is not None
    assert excinfo.value.response.code is None


@pytest.mark.parametrize(
    ("response", "expected_message"),
    [
        (FakeResponse(example("error_500.json"), status_code=500), "HTTP 500: An unhandled exception"),
        (FakeResponse(b"<html>Bad Gateway</html>", status_code=502), r"HTTP 502\.$"),
        (FakeResponse(b"", status_code=503), r"HTTP 503\.$"),
    ],
)
def test_other_errors_raise_the_base_api_error(
    monkeypatch: pytest.MonkeyPatch,
    response: FakeResponse,
    expected_message: str,
) -> None:
    """Other error statuses raise the base API error, with whatever detail the body had."""
    client = _build_client()
    _stub_session(client, monkeypatch, response)

    with pytest.raises(SSActivewearAPIError, match=expected_message) as excinfo:
        client.get_categories()

    assert type(excinfo.value) is SSActivewearAPIError
    assert excinfo.value.status_code == response.status_code


def test_rate_limit_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    """The remaining request allowance is tracked from each response."""
    client = _build_client()
    _stub_session(
        client,
        monkeypatch,
        FakeResponse(example("categories.json"), headers={"X-Rate-Limit-Remaining": "59"}),
        FakeResponse(example("categories.json")),
        FakeResponse(example("error_500.json"), status_code=500, headers={"X-Rate-Limit-Remaining": "57"}),
    )
    assert client.rate_limit_remaining is None

    client.get_categories()
    assert client.rate_limit_remaining == 59  # noqa: PLR2004

    client.get_categories()
    assert client.rate_limit_remaining == 59  # noqa: PLR2004

    with pytest.raises(SSActivewearAPIError):
        client.get_categories()
    assert client.rate_limit_remaining == 57  # noqa: PLR2004
