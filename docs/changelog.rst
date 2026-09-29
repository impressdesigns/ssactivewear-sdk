Changelog
=========

- :release:`1.0.0 <29th September 2026>`
- :feature:`-` Cover the whole S&S API: categories, brands, styles, products, inventory, specs, orders, payment
  profiles, invoices, returns, cross references, days in transit, and tracking.
- :feature:`-` Raise :class:`~ssactivewear_sdk.exceptions.SSActivewearNotFoundError` for 404s and
  :class:`~ssactivewear_sdk.exceptions.SSActivewearAPIError` for any other error status, each with the status code
  and the parsed error body.
- :feature:`-` Record the remaining rate limit allowance in ``SSActivewear.rate_limit_remaining``.
- :feature:`-` Document where the published S&S documentation is wrong, and how the SDK handles it, in
  :doc:`api-corrections`.
- :bug:`- major` Parse fields added to S&S payloads since 0.2.0 (such as ``retailPrice`` and ``mediaAssets``)
  instead of rejecting the response.
- :feature:`-` Switch the HTTP client from httpx to niquests. **Breaking:** ``SSActivewear`` now takes ``api_key``
  instead of ``token``, and raises :class:`ValueError` instead of :class:`TypeError` for invalid credentials.
- :feature:`-` **Breaking:** ``products()`` is now ``get_products()`` and ``submit_order()`` is now
  ``create_order()``. The order models were renamed: ``OrderRequestShippingAddress`` is now
  ``OrderShippingAddress``, ``OrderRequestOrderLine`` is now ``OrderLineRequest``, ``OrderRequestPaymentProfile``
  is now ``PaymentProfileReference``, ``OrderResponse`` is now ``Order``, ``OrderResponseLine`` is now
  ``OrderLine``, ``OrderResponseShippingAddress`` is now ``ShippingAddress``, ``OrderResponseContainer`` is now
  ``OrderSubmission``, and ``Warehouse`` is now ``ProductWarehouse``. Model fields are named after the S&S fields.
  Money and weights are :class:`~decimal.Decimal`, and the shipping method is a ``ShippingMethod`` enum.
- :release:`0.1.0 <7th October 2023>`
- :feature:`1` Initialize package
