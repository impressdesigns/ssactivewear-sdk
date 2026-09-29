Cross references
================

A cross reference maps one of your own sku numbers to an S&S sku. After that, you can use
your sku wherever the API takes a product identifier, and products report it as
``your_sku``.

.. code-block:: python

   created = ss.set_cross_reference("G2000whtxl", "B00760003")  # True if new, False if updated

   mappings = ss.get_cross_references()
   mapping = ss.get_cross_references("G2000whtxl")

   ss.delete_cross_reference("G2000whtxl")

The S&S side of a mapping can be a sku ID, a sku, or a GTIN. Your sku may only contain
letters, digits, hyphens, underscores, and spaces. Anything else raises :class:`ValueError`
before a request is sent.
