Returns
=======

Requesting a return
-------------------

Each returned sku names the invoice it was billed on and a
:class:`~ssactivewear_sdk.models.returns.ReturnReason`:

.. code-block:: python

   from ssactivewear_sdk import ReturnReason, ReturnRequest, ReturnRequestLine

   orders = ss.create_return(
       ReturnRequest(
           lines=[
               ReturnRequestLine(
                   invoice_number="43937002",
                   identifier="B00760003",
                   qty=2,
                   return_reason=ReturnReason.DAMAGED_OR_DEFECTIVE,
                   is_replace=True,
                   return_reason_comment="Torn seam on both shirts.",
               )
           ],
           email_confirmation="returns@example.com",
       )
   )

To replace an item returned as damaged or defective, or for any other reason, S&S needs a
comment. Leaving it out raises :class:`pydantic.ValidationError <pydantic_core.ValidationError>` when the line is built.

A return can come back as several orders. A credit order has an ``order_type`` of
``Credit``, and a replacement order has ``Replacement``.
:attr:`~ssactivewear_sdk.models.returns.ReturnOrder.return_information` has the RA number,
the return address, and the shipping label URL. With ``show_boxes=True`` it also has
per-box labels.

Cancelling
----------

S&S allows a return to be cancelled for 10 minutes after it was requested:

.. code-block:: python

   ss.cancel_return("9490497")

Looking returns up
------------------

.. code-block:: python

   from datetime import date

   returns = ss.get_returns("PO-1001", lines=True)
   returns = ss.get_returns(invoice_dates=date(2026, 9, 29), boxes=True)
