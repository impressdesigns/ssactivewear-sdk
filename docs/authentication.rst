Authentication
==============

S&S authenticates with HTTP basic auth: the user name is your account number and the
password is your API key. You can find the key under
`My Account <https://www.ssactivewear.com/myaccount>`_ on the S&S website. Keep it out of
source control.

.. code-block:: python

   from ssactivewear_sdk import SSActivewear

   ss = SSActivewear("12345", "0f8fad5b-d9cb-469f-a165-70867728950e")

The account number must be numeric and the API key must be a UUID. Anything else raises
:class:`ValueError` before a request is sent.

Timeouts
--------

Requests time out after 30 seconds. Pulling the whole catalog in one call
(:meth:`~ssactivewear_sdk.client.SSActivewear.get_products` without filters) returns a very
large payload, so give a client that does that a longer timeout:

.. code-block:: python

   ss = SSActivewear(account_number, api_key, timeout=600)
