Errors and rate limits
======================

Errors
------

Any error status from S&S raises
:class:`~ssactivewear_sdk.exceptions.SSActivewearAPIError` or one of its subclasses:

:class:`~ssactivewear_sdk.exceptions.SSActivewearBadRequestError`
   HTTP 400. Part of the request was invalid.
:class:`~ssactivewear_sdk.exceptions.SSActivewearNotFoundError`
   HTTP 404. None of the requested items exist, or they have been discontinued.

The exception carries the status code and, when the body was a recognizable error, the
parsed :class:`~ssactivewear_sdk.models.errors.ErrorResponse`, which lists each problem:

.. code-block:: python

   from ssactivewear_sdk import SSActivewearBadRequestError

   try:
       ss.create_order(order)
   except SSActivewearBadRequestError as error:
       for detail in error.response.errors if error.response else []:
           print(detail.field, detail.message)

Every exception the SDK raises for an API error derives from
:class:`~ssactivewear_sdk.exceptions.SSActivewearError`.

Rate limits
-----------

S&S allows 60 requests a minute. After each response, the client records how many are left
in :attr:`~ssactivewear_sdk.client.SSActivewear.rate_limit_remaining`. It is ``None`` until
S&S has reported it:

.. code-block:: python

   import time

   ss.get_categories()
   if ss.rate_limit_remaining is not None and ss.rate_limit_remaining < 5:
       time.sleep(60)
