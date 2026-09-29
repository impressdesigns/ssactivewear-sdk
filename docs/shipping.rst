Shipping
========

Days in transit
---------------

:meth:`~ssactivewear_sdk.client.SSActivewear.get_days_in_transit` gives each warehouse's
same-day cutoff time and the transit time to a ZIP code:

.. code-block:: python

   (transit,) = ss.get_days_in_transit("60440")
   for warehouse in transit.warehouses:
       print(warehouse.warehouse_abbr, warehouse.cut_off_time, warehouse.days_in_transit)

Tracking
--------

Look up the shipping status of orders by invoice number, order number, tracking number, ship
date, or delivery date:

.. code-block:: python

   from datetime import date

   tracking = ss.get_tracking_by_order_number(["32526736", "32526740"])
   tracking = ss.get_tracking_by_invoice("43937002", boxes=True)
   tracking = ss.get_tracking_by_ship_date_range(date(2026, 9, 1), date(2026, 9, 30))
   tracking = ss.get_tracking_by_delivery_date(date(2026, 9, 29))

With ``boxes=True``, a shipment with several boxes reports each box separately, with a
``box_number``. S&S doesn't document the tracking payload, so every field of
:class:`~ssactivewear_sdk.models.shipping.TrackingData` is optional.
