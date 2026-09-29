"""Interacting with S&S' API."""

import re
import uuid
from collections.abc import Iterable
from datetime import date
from email.message import Message
from http import HTTPStatus
from typing import Any, Literal
from urllib.parse import quote, urlencode

from niquests import Response, Session
from pydantic import TypeAdapter, ValidationError

from .exceptions import SSActivewearAPIError, SSActivewearBadRequestError, SSActivewearNotFoundError
from .models import (
    Brand,
    Category,
    CrossReference,
    DaysInTransit,
    ErrorResponse,
    InventoryItem,
    InvoicePDF,
    Order,
    OrderRequest,
    OrderSubmission,
    PaymentProfile,
    Product,
    ReturnOrder,
    ReturnRequest,
    Spec,
    Style,
    TrackingData,
)
from .models._base import SSActivewearBaseModel

DEFAULT_BASE_URL = "https://api.ssactivewear.com/v2"
DEFAULT_TIMEOUT = 30.0

# S&S allows 60 requests a minute and reports what is left of the allowance on every response.
RATE_LIMIT_HEADER = "X-Rate-Limit-Remaining"

# The documented character set for your own sku numbers.
YOUR_SKU_PATTERN = re.compile(r"[A-Za-z0-9_\- ]+")

type Identifier = str | int
type Identifiers = Identifier | Iterable[Identifier]
"""One identifier, or several. S&S takes several as a comma separated list."""
type Dates = date | Iterable[date]
"""One date, or several."""

_BRANDS = TypeAdapter(list[Brand])
_CATEGORIES = TypeAdapter(list[Category])
_CROSS_REFERENCES = TypeAdapter(list[CrossReference])
_DAYS_IN_TRANSIT = TypeAdapter(list[DaysInTransit])
_INVENTORY = TypeAdapter(list[InventoryItem])
_ORDERS = TypeAdapter(list[Order])
_ORDER_SUBMISSION: TypeAdapter[list[Order] | OrderSubmission] = TypeAdapter(list[Order] | OrderSubmission)
_PRODUCTS = TypeAdapter(list[Product])
_RETURNS = TypeAdapter(list[ReturnOrder])
_SPECS = TypeAdapter(list[Spec])
_STYLES = TypeAdapter(list[Style])
# The documentation shows these two wrapped in an extra list; accept either shape.
_PAYMENT_PROFILES: TypeAdapter[list[PaymentProfile] | list[list[PaymentProfile]]] = TypeAdapter(
    list[PaymentProfile] | list[list[PaymentProfile]]
)
_TRACKING: TypeAdapter[list[TrackingData] | list[list[TrackingData]]] = TypeAdapter(
    list[TrackingData] | list[list[TrackingData]]
)


class SSActivewear:
    """A class wrapping S&S' API."""

    def __init__(
        self,
        account_number: str,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client.

        Parameters
        ----------
        account_number
            Your S&S account number, sent as the basic auth user name.
        api_key
            Your S&S API key, sent as the basic auth password.
        base_url
            The API root.
        timeout
            Seconds to wait for a response. Unfiltered catalog requests return very large
            payloads, so raise this for a client that pulls the whole catalog.
        """
        if not account_number.isdigit():
            message = "account_number must be your numeric S&S account number."
            raise ValueError(message)
        try:
            uuid.UUID(api_key)
        except ValueError as exception:
            message = "api_key must be the API key (a UUID) from your S&S account."
            raise ValueError(message) from exception

        self.client = Session(
            base_url=base_url,
            timeout=timeout,
            auth=(account_number, api_key),
        )
        self.rate_limit_remaining: int | None = None
        """Requests left in the current rate limit window, as of the last response."""

    def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        """Make a request to S&S, raising for an error status."""
        if params:
            # Encode the query string by hand so comma separated lists keep literal commas and
            # spaces become %20, exactly as S&S documents them (``?Warehouses=IL,KS``).
            path = f"{path}?{urlencode(params, safe=',', quote_via=quote)}"
        response = self.client.request(method=method, url=path, json=json)

        remaining = response.headers.get(RATE_LIMIT_HEADER)
        if remaining is not None and remaining.isdigit():
            self.rate_limit_remaining = int(remaining)

        if not response.ok:
            raise _api_error(response)
        return response

    def _get[T](self, path: str, adapter: TypeAdapter[T], params: dict[str, str] | None = None) -> T:
        """GET a JSON resource and validate it."""
        response = self._make_request("GET", path, params=params)
        return adapter.validate_json(_content(response))

    # -----------------------------------------------------------------------------------------
    # Catalog
    # -----------------------------------------------------------------------------------------

    def get_categories(self, category_ids: Identifiers | None = None) -> list[Category]:
        """Get every category, or only the categories with the given IDs."""
        return self._get(_path("categories", category_ids), _CATEGORIES)

    def get_brands(self, brand_ids: Identifiers | None = None) -> list[Brand]:
        """Get every brand, or only the brands with the given IDs."""
        return self._get(_path("Brands", brand_ids), _BRANDS)

    def get_styles(
        self,
        identifiers: Identifiers | None = None,
        *,
        search: str | None = None,
        style_ids: Identifiers | None = None,
        part_numbers: Identifiers | None = None,
    ) -> list[Style]:
        """Get styles.

        Parameters
        ----------
        identifiers
            Style IDs, part numbers, or ``"{brand name} {style name}"`` names, e.g. ``"Gildan 5000"``.
        search
            Free text search, e.g. ``"Gildan 2000"``.
        style_ids
            Style IDs.
        part_numbers
            Part numbers (the first 5 digits of a sku).
        """
        params = _query(search=search, styleid=style_ids, partnumber=part_numbers)
        return self._get(_path("styles", identifiers), _STYLES, params)

    def get_products(
        self,
        identifiers: Identifiers | None = None,
        *,
        styles: Identifiers | None = None,
        style_ids: Identifiers | None = None,
        part_numbers: Identifiers | None = None,
        warehouses: Identifiers | None = None,
    ) -> list[Product]:
        """Get products (skus) with pricing and stock.

        With no filters this returns the entire catalog, which is very large.

        Parameters
        ----------
        identifiers
            Sku IDs, skus, GTINs, or your skus.
        styles
            Style IDs, part numbers, or ``"{brand name} {style name}"`` names.
        style_ids
            Style IDs.
        part_numbers
            Part numbers (the first 5 digits of a sku).
        warehouses
            Only report stock in these warehouses, e.g. ``["IL", "KS"]``.
        """
        params = _query(style=styles, styleid=style_ids, partnumber=part_numbers, Warehouses=warehouses)
        return self._get(_path("products", identifiers), _PRODUCTS, params)

    def get_inventory(
        self,
        identifiers: Identifiers | None = None,
        *,
        styles: Identifiers | None = None,
        style_ids: Identifiers | None = None,
        part_numbers: Identifiers | None = None,
        warehouses: Identifiers | None = None,
    ) -> list[InventoryItem]:
        """Get warehouse stock. Takes the same filters as :meth:`get_products` and returns far less data."""
        params = _query(style=styles, styleid=style_ids, partnumber=part_numbers, Warehouses=warehouses)
        return self._get(_path("inventory", identifiers), _INVENTORY, params)

    def get_specs(self, spec_ids: Identifiers | None = None, *, styles: Identifiers | None = None) -> list[Spec]:
        """Get spec sheet entries, by spec ID or by style (ID, part number, or ``"{brand} {style}"``)."""
        return self._get(_path("specs", spec_ids), _SPECS, _query(style=styles))

    # -----------------------------------------------------------------------------------------
    # Orders
    # -----------------------------------------------------------------------------------------

    def get_orders(  # noqa: PLR0913
        self,
        identifiers: Identifiers | None = None,
        *,
        include_invoiced: bool = False,
        invoice_dates: Dates | None = None,
        invoice_date_range: tuple[date, date] | None = None,
        shipping_label_barcode: str | None = None,
        lines: bool = False,
        boxes: bool = False,
        billing: bool = False,
        include_ar_child_invoices: bool = False,
        sort_by: Literal["linenumber", "packing"] | None = None,
    ) -> list[Order]:
        """Get orders.

        With no arguments this returns every order that has not been invoiced yet.

        Parameters
        ----------
        identifiers
            PO numbers, order numbers, invoice numbers, or order GUIDs.
        include_invoiced
            Also return invoiced orders from the last 3 months.
        invoice_dates
            Orders invoiced on these dates.
        invoice_date_range
            Orders invoiced between these two dates.
        shipping_label_barcode
            The order a shipping label belongs to (``{invoice number}.{box number}{lane}``).
        lines
            Include each order's lines.
        boxes
            Include each order's boxes.
        billing
            Include each order's billing address.
        include_ar_child_invoices
            Also return orders for AR child accounts.
        sort_by
            Line order: by line number, or packing order (S&S's default).
        """
        start, end = invoice_date_range if invoice_date_range is not None else (None, None)
        params = _query(
            All=include_invoiced,
            invoicedate=_dates_or_none(invoice_dates),
            invoicestartdate=_dates_or_none(start),
            invoiceenddate=_dates_or_none(end),
            shippinglabelbarcode=shipping_label_barcode,
            lines=lines,
            Boxes=boxes,
            Billing=billing,
            includeARChildInvoices=include_ar_child_invoices,
            sortby=sort_by,
        )
        return self._get(_path("orders", identifiers), _ORDERS, params)

    def create_order(self, order: OrderRequest) -> OrderSubmission:
        """Place an order.

        S&S splits an order that ships from several warehouses into one order per warehouse.
        """
        response = self._make_request("POST", "/orders/", json=_request_body(order))
        result = _ORDER_SUBMISSION.validate_json(_content(response))
        if isinstance(result, OrderSubmission):
            return result
        return OrderSubmission(orders=result)

    def cancel_order(self, order_number: Identifier) -> list[Order]:
        """Cancel an order. S&S allows this up to 10 minutes after the order was placed.

        Returns the orders that were cancelled.
        """
        response = self._make_request("DELETE", _path("orders", order_number))
        return _ORDERS.validate_json(_content(response))

    def get_payment_profiles(self, email: str) -> list[PaymentProfile]:
        """Get the credit cards and bank accounts saved under a website user."""
        return _flatten(self._get("/paymentprofiles/", _PAYMENT_PROFILES, {"email": email}))

    # -----------------------------------------------------------------------------------------
    # Invoices
    # -----------------------------------------------------------------------------------------

    def get_invoice_pdf(self, invoice_number: Identifier) -> InvoicePDF:
        """Get one invoice as a PDF."""
        return self._get_pdf(_path("Invoices", invoice_number))

    def get_invoice_pdf_by_guid(self, guid: uuid.UUID | str) -> InvoicePDF:
        """Get the invoice for an order GUID as a PDF."""
        return self._get_pdf("/Invoices/", {"Guid": str(guid)})

    def get_invoice_pdf_by_order_number(self, order_number: Identifier) -> InvoicePDF:
        """Get every invoice for an order number, combined into one PDF."""
        return self._get_pdf("/Invoices/", {"OrderNumber": str(order_number)})

    def _get_pdf(self, path: str, params: dict[str, str] | None = None) -> InvoicePDF:
        """GET a PDF document."""
        response = self._make_request("GET", path, params=params)
        return InvoicePDF(
            filename=_attachment_filename(response.headers.get("Content-Disposition")),
            content=_content(response),
        )

    # -----------------------------------------------------------------------------------------
    # Returns
    # -----------------------------------------------------------------------------------------

    def get_returns(
        self,
        identifiers: Identifiers | None = None,
        *,
        invoice_dates: Dates | None = None,
        lines: bool = False,
        boxes: bool = False,
    ) -> list[ReturnOrder]:
        """Get return and replacement orders.

        Parameters
        ----------
        identifiers
            PO numbers (of the original order), order numbers, invoice numbers, or order GUIDs.
        invoice_dates
            Returns invoiced on these dates.
        lines
            Include each order's lines.
        boxes
            Include each order's boxes.
        """
        params = _query(invoicedate=_dates_or_none(invoice_dates), lines=lines, Boxes=boxes)
        return self._get(_path("returns", identifiers), _RETURNS, params)

    def create_return(self, request: ReturnRequest) -> list[ReturnOrder]:
        """Request a return.

        Depending on the return and whether replacements were asked for, S&S may create both a
        credit order and a replacement order.
        """
        response = self._make_request("POST", "/returns/", json=_request_body(request))
        return _RETURNS.validate_json(_content(response))

    def cancel_return(self, order_number: Identifier) -> list[ReturnOrder]:
        """Cancel a return. S&S allows this up to 10 minutes after the return was requested.

        Returns the orders that were cancelled.
        """
        response = self._make_request("DELETE", _path("returns", order_number))
        return _RETURNS.validate_json(_content(response))

    # -----------------------------------------------------------------------------------------
    # Cross references
    # -----------------------------------------------------------------------------------------

    def get_cross_references(self, your_skus: Identifiers | None = None) -> list[CrossReference]:
        """Get every sku you have mapped to your own sku, or only the given ones."""
        return self._get(_path("crossref", your_skus), _CROSS_REFERENCES)

    def set_cross_reference(self, your_sku: str, identifier: Identifier) -> bool:
        """Map your sku to an S&S sku (sku ID, sku, or GTIN), replacing any existing mapping.

        Returns ``True`` if the mapping was created and ``False`` if an existing one was updated.
        """
        _validate_your_sku(your_sku)
        response = self._make_request("PUT", _path("crossref", your_sku), params={"Identifier": str(identifier)})
        return response.status_code == HTTPStatus.CREATED

    def delete_cross_reference(self, your_sku: str) -> None:
        """Remove the mapping for your sku."""
        _validate_your_sku(your_sku)
        self._make_request("DELETE", _path("crossref", your_sku))

    # -----------------------------------------------------------------------------------------
    # Shipping
    # -----------------------------------------------------------------------------------------

    def get_days_in_transit(self, zip_codes: Identifiers | None = None) -> list[DaysInTransit]:
        """Get cutoff times and days in transit from each warehouse, for every ZIP code or only the given ones."""
        return self._get(_path("daysintransit", zip_codes), _DAYS_IN_TRANSIT)

    def get_all_tracking(self, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for every shipment."""
        return self._get_tracking("/TrackingDataGetAll/", boxes=boxes)

    def get_tracking_by_invoice(self, invoice_numbers: Identifiers, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for invoice numbers."""
        return self._get_tracking(_path("TrackingDataByInvoice", invoice_numbers), boxes=boxes)

    def get_tracking_by_order_number(self, order_numbers: Identifiers, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for order numbers."""
        return self._get_tracking(_path("TrackingDataByOrderNum", order_numbers), boxes=boxes)

    def get_tracking_by_tracking_number(
        self,
        tracking_numbers: Identifiers,
        *,
        boxes: bool = False,
    ) -> list[TrackingData]:
        """Get tracking data for tracking numbers."""
        return self._get_tracking(_path("TrackingDataByTrackingNum", tracking_numbers), boxes=boxes)

    def get_tracking_by_ship_date(self, ship_dates: Dates, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for shipments that shipped on the given dates."""
        return self._get_tracking(_path("TrackingDataByShipDate", _date_list(ship_dates)), boxes=boxes)

    def get_tracking_by_ship_date_range(self, start: date, end: date, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for shipments that shipped between two dates."""
        return self._get_tracking(_path("TrackingDataByShippingDateRange", _date_list([start, end])), boxes=boxes)

    def get_tracking_by_delivery_date(self, delivery_dates: Dates, *, boxes: bool = False) -> list[TrackingData]:
        """Get tracking data for shipments that were delivered on the given dates."""
        return self._get_tracking(_path("TrackingDataByActualDeliveryDate", _date_list(delivery_dates)), boxes=boxes)

    def _get_tracking(self, path: str, *, boxes: bool) -> list[TrackingData]:
        """GET tracking data. With ``boxes``, shipments with several boxes report each box."""
        return _flatten(self._get(path, _TRACKING, _query(Boxes=boxes)))


def _identifier_list(identifiers: Identifiers) -> list[str]:
    """Normalize one or several identifiers into a list of strings."""
    values = [identifiers] if isinstance(identifiers, str | int) else list(identifiers)
    if not values:
        message = "At least one identifier is required."
        raise ValueError(message)

    identifier_list = []
    for value in values:
        text = str(value)
        if not text.strip():
            message = "Identifiers must not be blank."
            raise ValueError(message)
        if "," in text:
            message = f"Identifier {text!r} must not contain a comma; S&S uses commas to separate identifiers."
            raise ValueError(message)
        identifier_list.append(text)
    return identifier_list


def _path(resource: str, identifiers: Identifiers | None = None) -> str:
    """Build a resource path, with identifiers percent-encoded into the last segment."""
    if identifiers is None:
        return f"/{resource}/"
    return f"/{resource}/" + ",".join(quote(identifier, safe="") for identifier in _identifier_list(identifiers))


def _query(**values: Identifiers | bool | None) -> dict[str, str]:
    """Build query parameters, dropping unset values and flags that are off."""
    params = {}
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                params[key] = "true"
            continue
        params[key] = ",".join(_identifier_list(value))
    return params


def _date_list(dates: Dates) -> list[str]:
    """Format one or several dates the way S&S expects (``yyyy-MM-dd``)."""
    values = [dates] if isinstance(dates, date) else list(dates)
    if not values:
        message = "At least one date is required."
        raise ValueError(message)
    return [value.strftime("%Y-%m-%d") for value in values]


def _dates_or_none(dates: Dates | None) -> list[str] | None:
    """Format dates when given."""
    return None if dates is None else _date_list(dates)


def _request_body(model: SSActivewearBaseModel) -> dict[str, Any]:
    """Serialize a request, leaving unset fields to S&S' defaults."""
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)


def _content(response: Response) -> bytes:
    """Return the response body."""
    return response.content or b""


def _flatten[ModelT: SSActivewearBaseModel](items: list[ModelT] | list[list[ModelT]]) -> list[ModelT]:
    """Unwrap a response that arrived as a list of lists."""
    flat: list[ModelT] = []
    for item in items:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)
    return flat


def _attachment_filename(content_disposition: str | None) -> str | None:
    """Pull the file name out of a ``Content-Disposition`` header."""
    if not content_disposition:
        return None
    message = Message()
    message["Content-Disposition"] = content_disposition
    return message.get_filename()


def _validate_your_sku(your_sku: str) -> None:
    """Check your sku against the characters S&S allows."""
    if YOUR_SKU_PATTERN.fullmatch(your_sku) is None:
        message = f"your_sku {your_sku!r} may only contain letters, digits, hyphens, underscores, and spaces."
        raise ValueError(message)


def _api_error(response: Response) -> SSActivewearAPIError:
    """Build the exception for an error response."""
    status_code = response.status_code or 0
    error_response = _parse_error(_content(response))
    detail = error_response.describe() if error_response is not None else None
    message = f"S&S returned HTTP {status_code}: {detail}" if detail else f"S&S returned HTTP {status_code}."
    error_class: type[SSActivewearAPIError]
    match status_code:
        case HTTPStatus.BAD_REQUEST:
            error_class = SSActivewearBadRequestError
        case HTTPStatus.NOT_FOUND:
            error_class = SSActivewearNotFoundError
        case _:
            error_class = SSActivewearAPIError
    return error_class(message, status_code=status_code, response=error_response)


def _parse_error(content: bytes) -> ErrorResponse | None:
    """Parse an error body, if it is one."""
    if not content:
        return None
    try:
        return ErrorResponse.model_validate_json(content)
    except ValidationError:
        return None
