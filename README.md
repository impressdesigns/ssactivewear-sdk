# S&S Activewear SDK

A typed wrapper for the [S&S Activewear API](https://api.ssactivewear.com/V2/): catalog, inventory, orders,
invoices, returns, cross references, days in transit, and tracking.

```python
from ssactivewear_sdk import SSActivewear

ss = SSActivewear(account_number="12345", api_key="0f8fad5b-d9cb-469f-a165-70867728950e")
for product in ss.get_products(styles="Gildan 5000", warehouses=["IL", "KS"]):
    print(product.sku, product.customer_price, product.qty)
```

Documentation, including the places where the published S&S documentation is wrong, is at
https://impressdesigns.dev/ssactivewear-sdk/.
