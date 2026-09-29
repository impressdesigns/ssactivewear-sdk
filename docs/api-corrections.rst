API documentation corrections
=============================

The `published S&S API documentation <https://api.ssactivewear.com/V2/>`_ contradicts itself
in places. On a single page the example payload, the object definition table, and the
request examples can each say something different. This page lists every such case the SDK
has to take a position on, what it does, and why.

Four sources were compared:

Definition
   The object definition table on each page.
Example
   The example request and response on each page.
Link
   The target of the page's clickable "try it" links. These open the real endpoint, and
   sometimes disagree with the link text shown next to them.
Sample
   The C# and VB.net code samples on the `Code Examples
   <https://api.ssactivewear.com/V2/Help_Examples.aspx>`_ page. The two samples are
   identical field for field. They predate several current fields, so they are only
   evidence for the fields they do contain.

None of these corrections were checked against the live API. Where the evidence doesn't
settle a question, the SDK accepts every documented shape instead of picking one, and the
entry says so. The documented examples ship with the test suite in ``tests/examples/``, and
the tests check the SDK's handling of each correction that affects a request or a response.

General
-------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - Error bodies have ``code``, ``message`` and ``errors`` (Help - Errors).
     - Treats every field of :class:`~ssactivewear_sdk.models.errors.ErrorResponse` as
       optional. A not-found 404 carries only ``errors``, and a routing 404 carries
       ``message`` and ``messageDetail``.
     - Example: the "Not Found Response" on the Products and Inventory pages, and the 404 on
       Help - Errors.
   * - "If you receive a 404 Bad Request response, please validate your json request" (POST -
       Orders, POST - Returns).
     - Treats Bad Request as HTTP 400 and raises
       :class:`~ssactivewear_sdk.exceptions.SSActivewearBadRequestError`. A 404 raises
       :class:`~ssactivewear_sdk.exceptions.SSActivewearNotFoundError`.
     - Help - Errors documents 400 as Bad Request and 404 as a wrong resource URL.
   * - ``/v2/inventory/?style=bella + canvas 3001cvc`` (GET - Inventory).
     - Percent-encodes identifiers and query values: ``bella%20%2B%20canvas%203001cvc``. An
       unencoded ``+`` in a query string decodes to a space, so the brand name would be lost.
     - Example: GET - Products shows the encoded form, and says special characters and spaces
       "will need to be encoded".
   * - Lists of identifiers or filter values are comma separated.
     - Sends commas literally (``?Warehouses=IL,KS``) and rejects an identifier that
       contains a comma, since S&S would split it in two.
     - Example and Link, on every page.
   * - The Help - Errors 404 example is for ``https://apidev.ssactivewear.com/V1/orderss``.
     - Nothing; the host and version in that example are irrelevant.
     - Every other page uses ``https://api.ssactivewear.com/v2``.
   * - The code samples place orders with a ``CreditCard`` object (``cardNumber``,
       ``expMonth``, …).
     - Follows the current POST - Orders page, which pays with ``paymentProfile``
       (:class:`~ssactivewear_sdk.models.orders.PaymentProfileReference`) and doesn't mention
       card numbers.
     - Definition. The samples are older than the current documentation.

Styles
------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - The field is ``baseCateogry``.
     - Reads ``baseCategory``, and also accepts the misspelling.
     - Example and Sample both spell it ``baseCategory``.
   * - ``comparableGroup`` and ``companionGroup`` are Strings.
     - Parses them as integers (``None`` when missing or blank), and also accepts numeric
       strings.
     - Example (``7``, ``2``) and Sample (``int?``).
   * - Media assets carry ``asset_type``.
     - Accepts both ``asset_type`` and ``assetType``.
     - The Styles example sends ``assetType``; the Products example sends ``asset_type``.
   * - Search is ``/v2/styles/search={value}``.
     - Sends ``/v2/styles/?search={value}``.
     - Link targets ``styles?search=Gildan 2000``, and the row's own second example uses
       ``?search=``.
   * - The Filter Fields example requests ``?fields=BrandName,Name,Title``.
     - Doesn't expose ``fields``: a partial payload can't fill a typed model. There is no
       ``Name`` field on a style; the name is ``styleName``.
     - Definition.

Products
--------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - ``brandID`` and ``colorFamilyID`` are Integers.
     - Keeps them as strings, as they are sent, and also accepts integers.
       ``baseCategoryID`` and ``colorGroup`` are handled the same way.
     - Example (``"35"``, ``"19"``, ``"16"``, ``"79"``).
   * - ``baseCategoryID`` isn't in the object definition.
     - Parses it.
     - Example.
   * - ``saleExpiration`` is a String in ``MM/DD/YYYY`` form.
     - Parses it as a :class:`~datetime.datetime`, accepting ISO 8601 or ``MM/DD/YYYY``.
       An empty value means no sale.
     - Example (``"2026-07-30T00:00:00"``) and Sample (``DateTime?``).
   * - The field is ``PolyPackQty``.
     - Reads ``polyPackQty``, and also accepts ``PolyPackQty``.
     - Example.
   * - ``asset_type`` is one of Style, Front, Back, Direct Side, On Model Front, On Model
       Back, On Model Side.
     - Keeps ``asset_type`` as a plain string.
     - The Example sends ``DirectSide``, ``OnModel_Front``, ``OnModel_Back`` and
       ``OnModel_Side``.
   * - Filtering warehouses is ``/v2/products/B00760003?Warehouses?{WarehouseAbbr}``. The
       same appears on GET - Inventory.
     - Sends ``?Warehouses=IL,KS``.
     - Link, and the row's own second example.
   * - ``retailPrice`` is a product field.
     - Parses it, but as optional. The code samples and earlier versions of the
       documentation don't have it.
     - Definition and Example.
   * - The code samples call the size code ``sieCode``.
     - Reads ``sizeCode``; the typo is in the samples.
     - Definition and Example.

Inventory
---------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - The inventory item's ID is ``skuID``.
     - Reads ``skuID_Master`` into ``sku_id_master``, and also accepts ``skuID``.
     - Example.

Specs, Brands, and Days in Transit
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - The Specs Filter Fields example is ``/v2/spec/39?fields=…``.
     - Uses ``/v2/specs/``.
     - Link targets ``specs/39?fields=…``, like every other Specs request.
   * - Specs "Get All" "Returns all styles".
     - Returns specs.
     - Example.
   * - Brands filtering takes "a comma separated list of category identifiers".
     - Takes brand IDs.
     - Example (``/v2/Brands/31``).
   * - Days in Transit "Returns all categories" and filters by ``{category}``, "a comma
       separated list of category identifiers".
     - Takes ZIP codes.
     - Example (``/v2/daysintransit/60440``) and the same row's "identifiers = zipcode".
   * - The Days in Transit ``warehouses`` field is an Object.
     - Parses a list.
     - Example.

Orders
------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - ``totalBoxes`` is a Decimal.
     - Parses an integer, and also accepts integral decimals.
     - Example (``1``) and Sample (``int?``).
   * - The order object is fully described by the definition.
     - Also parses ``expectedDeliveryDate`` and ``conveyorLane``, and the
       ``orderHeaderID`` that appears in the code samples.
     - Example (POST - Orders, GET - Returns) and Sample.
   * - ``orderStatus`` is one of InProgress, Shipped, Completed, Canceled. ``orderType`` is
       one of CSR, Web, EDI, Credit.
     - Keeps both as plain strings.
     - The Examples send ``In Progress``, ``Cancelled`` and ``Credit`` statuses, and ``API``
       and ``Replacement`` types.
   * - ``warehouseAbbr`` is one of IL, NV, NJ, KS, GA, TX, FL, OH, DS.
     - Keeps it as a plain string.
     - POST - Orders lists PA, CC, CN, FO and MA as well, and the Products example has
       warehouses PA, CN, FO and MA.
   * - The definition row for the invoice number is named ``invoice Number``.
     - Reads ``invoiceNumber``.
     - Example.
   * - ``?Boxes=true`` returns each order's boxes; the box object isn't defined on the Orders
       page.
     - Uses the box definition from GET - Returns for both
       (:class:`~ssactivewear_sdk.models.orders.Box`).
     - Definition on GET - Returns.
   * - Some fields appear in one example and not another. For example, GET - Orders has
       ``lostCashDiscount`` and ``shipDate``; POST - Orders has ``expectedDeliveryDate``;
       DELETE - Orders has neither ``shippingSaved`` nor ``deliveryStatus``.
     - Makes every field that isn't in all of the examples optional.
     - Example.
   * - The POST - Orders response example is not valid JSON. It has ``XX.XX`` amounts and a
       ``XXXXXXXX-XXXX-…`` GUID.
     - Nothing to do; ``tests/examples/orders_create.json`` substitutes real values.
     - Example.
   * - With ``rejectLineErrors=false`` "the response body will contain both a list of Orders
       and LineErrors". There is no example of the shape.
     - Accepts ``orders``/``Orders`` and ``lineErrors``/``LineErrors``, and keeps each line
       error as raw JSON in
       :attr:`~ssactivewear_sdk.models.orders.OrderSubmission.line_errors`. **Unverified.**
     - None; every other response uses camelCase names.

Payment profiles
----------------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - The field is ``profyleType``, in a table titled "Category Object Definition".
     - Reads ``profileType``, and also accepts the misspelling.
     - Example.
   * - The response is a list inside a list: ``[[{…}]]``.
     - Accepts a nested or a flat list, and returns a flat list either way.
       **Unverified**; this may be a typo.
     - Example. Every other endpoint returns a flat list.

Invoices
--------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - Get by order GUID is ``/v2/Brands/?Guid=…``, and get by order number is
       ``/v2/Brands/?OrderNumber=…``.
     - Uses ``/v2/Invoices/?Guid=…`` and ``/v2/Invoices/?OrderNumber=…``.
     - Link targets ``Invoices/?Guid=…`` and ``Invoices/?OrderNumber=…``, and the rows'
       templates use ``/v2/Invoices/``.

Returns
-------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - ``returnItemsRequired`` is a Boolean.
     - Parses a boolean, and also accepts ``"true"``/``"false"``.
     - Example (``"true"``).
   * - ``totalPieces`` is an Integer (from GET - Orders).
     - Parses an integer, and also accepts integral decimals.
     - Example (``-20.00``).
   * - The box object is fully described by the definition.
     - Also parses ``boxRequired``.
     - Example.
   * - Box lines have ``price`` and ``returnable``.
     - Makes both optional.
     - The Example's box lines have neither.
   * - The POST example sends ``"invoiceNumber": 0000000``, ``"Qty"`` and
       ``"returnReason": 2``.
     - Sends ``invoiceNumber`` as a string, ``qty``, and ``returnReason`` as a string code
       (``"2"``), as the definition says. ``0000000`` isn't valid JSON.
     - Definition.
   * - GET - Returns has no "Get All" option.
     - Allows :meth:`~ssactivewear_sdk.client.SSActivewear.get_returns` without filters,
       which requests ``/v2/returns/`` as GET - Orders does. **Unverified.**
     - None.
   * - The DELETE - Returns example is a copy of the DELETE - Orders example
       (``orderType`` ``API``).
     - Parses it as a :class:`~ssactivewear_sdk.models.returns.ReturnOrder`, without
       return information.
     - Example.

Cross references
----------------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - PUT takes ``yourSku`` and ``identifier``, without saying where.
     - Puts ``yourSku`` in the path and ``Identifier`` in the query string, with an empty
       body.
     - Example (``/v2/crossref/G2000whtxl?Identifier=B00760003``) and Sample (the same URL,
       with ``ContentLength = 0``).
   * - The Filter Fields example asks for ``ColorNameSizeName``.
     - Doesn't expose ``fields``. The example is missing a comma between ``ColorName`` and
       ``SizeName``.
     - Definition.
   * - The cross reference object has eight fields.
     - Ignores the ``customerID`` field that the code samples also have.
     - Sample.

Tracking
--------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - The documentation says
     - The SDK does
     - Evidence
   * - Nothing about the tracking object: the page has no object definition.
     - Models the fields in the example
       (:class:`~ssactivewear_sdk.models.shipping.TrackingData`), with every field optional
       and ``boxNumber`` added for ``?Boxes=true``.
     - Example, and the "Include Boxes" row.
   * - The response is ``[[{…}]`` (unbalanced).
     - Accepts a nested or a flat list, and returns a flat list either way.
       **Unverified.**
     - Example.
