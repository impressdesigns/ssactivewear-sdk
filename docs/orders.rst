Orders
======

Placing an order
----------------

Build an :class:`~ssactivewear_sdk.models.orders.OrderRequest` and pass it to
:meth:`~ssactivewear_sdk.client.SSActivewear.create_order`:

.. code-block:: python

   from ssactivewear_sdk import OrderLineRequest, OrderRequest, OrderShippingAddress, ShippingMethod

   submission = ss.create_order(
       OrderRequest(
           shipping_address=OrderShippingAddress(
               customer="Company ABC",
               attn="John Doe",
               address="123 Main St",
               city="Bolingbrook",
               state="IL",
               zip="60440",
           ),
           lines=[OrderLineRequest(identifier="B00760003", qty=2)],
           shipping_method=ShippingMethod.UPS_GROUND,
           po_number="PO-1001",
           autoselect_warehouse=True,
       )
   )
   for order in submission.orders:
       print(order.order_number, order.warehouse_abbr, order.total)

Only the shipping address and lines are required. Every optional field you leave unset is
left out of the request, so S&S applies its own default. Pass ``test_order=True`` to try an
order without placing it: S&S creates the order and cancels it straight away.

S&S places one order per warehouse, so a single request can come back as several orders.
By default S&S rejects the whole request if any line can't be filled. With
``reject_line_errors=False`` it places what it can and reports the rest in
:attr:`~ssactivewear_sdk.models.orders.OrderSubmission.line_errors`.

To pay with a saved card or bank account, look up its profile ID first:

.. code-block:: python

   from ssactivewear_sdk import PaymentProfileReference

   (profile,) = ss.get_payment_profiles("buyer@example.com")
   payment_profile = PaymentProfileReference(email="buyer@example.com", profile_id=profile.profile_id)

Cancelling
----------

S&S allows an order to be cancelled for 10 minutes after it was placed:

.. code-block:: python

   cancelled = ss.cancel_order("9490497")

Looking orders up
-----------------

Without arguments, :meth:`~ssactivewear_sdk.client.SSActivewear.get_orders` returns every
order that hasn't been invoiced yet. Pass ``include_invoiced=True`` to also get the last 3
months of invoiced orders. You can also look orders up by PO number, order number, invoice
number, or GUID, or by invoice date:

.. code-block:: python

   from datetime import date

   orders = ss.get_orders(["PO-1001", "4629304"], lines=True, boxes=True)
   orders = ss.get_orders(invoice_date_range=(date(2026, 9, 1), date(2026, 9, 30)))
   orders = ss.get_orders(shipping_label_barcode="57926652.0031")

Lines, boxes, and the billing address are only included when asked for (``lines=True``,
``boxes=True``, ``billing=True``). ``ship_date``, ``invoice_date`` and ``tracking_number``
are only set once the order has shipped or been invoiced.

Invoices
--------

Invoices come back as PDF documents:

.. code-block:: python

   from pathlib import Path

   invoice = ss.get_invoice_pdf("83713072")
   Path(invoice.filename or "invoice.pdf").write_bytes(invoice.content)

:meth:`~ssactivewear_sdk.client.SSActivewear.get_invoice_pdf_by_guid` finds the invoice for
an order GUID.
:meth:`~ssactivewear_sdk.client.SSActivewear.get_invoice_pdf_by_order_number` combines every
invoice for an order number into one PDF.
