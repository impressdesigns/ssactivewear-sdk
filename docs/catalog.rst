Catalog
=======

Every catalog call is a method on :class:`~ssactivewear_sdk.client.SSActivewear`. Build one
as described in :doc:`authentication` first.

Identifiers
-----------

Wherever a method takes identifiers, pass one identifier or a list of them. Strings and
integers both work, and the SDK takes care of the comma separated lists and URL encoding S&S
expects:

.. code-block:: python

   ss.get_products("B00760004")
   ss.get_products([81480, "B00760004", "00821780008137"])
   ss.get_products(styles="bella + canvas 3001cvc")

Styles can be identified by style ID, part number (the first five digits of a sku), or brand
and style name together, such as ``"Gildan 5000"``.

Products
--------

:meth:`~ssactivewear_sdk.client.SSActivewear.get_products` returns a
:class:`~ssactivewear_sdk.models.products.Product` per sku. Each product has its pricing and
its stock in each warehouse. Filter by sku (ID, sku, GTIN, or your own sku) or by style, and
optionally limit the warehouses reported:

.. code-block:: python

   products = ss.get_products(styles="Gildan 5000", warehouses=["IL", "KS"])
   for product in products:
       print(product.sku, product.color_name, product.size_name, product.customer_price)
       for warehouse in product.warehouses:
           print("  ", warehouse.warehouse_abbr, warehouse.qty)

Prices and weights are :class:`~decimal.Decimal`. Images are paths relative to
``https://www.ssactivewear.com/``.

Inventory
---------

When you only need stock levels,
:meth:`~ssactivewear_sdk.client.SSActivewear.get_inventory` takes the same filters and
returns far less data:

.. code-block:: python

   for item in ss.get_inventory(part_numbers="00760"):
       print(item.sku, sum(warehouse.qty for warehouse in item.warehouses))

Styles
------

.. code-block:: python

   styles = ss.get_styles("Gildan 2000")
   styles = ss.get_styles(search="hooded sweatshirt")
   styles = ss.get_styles(style_ids=[39, 40])

:attr:`~ssactivewear_sdk.models.products.Style.category_ids` parses a style's comma separated
category list.

Categories, brands, and specs
-----------------------------

.. code-block:: python

   categories = ss.get_categories()
   brands = ss.get_brands([31, 35])
   specs = ss.get_specs(styles="Gildan 5000")

Each method returns everything when called without filters.
