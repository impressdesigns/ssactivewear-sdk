# Documented examples

Each file is the example from https://api.ssactivewear.com/V2 named below, copied verbatim
apart from whitespace. The published examples that are not valid JSON were repaired as
little as possible, as noted. These repairs are documentation errors, listed in
`docs/api-corrections.rst`.

| File | Page | Repair |
|---|---|---|
| `brands.json` | GET - Brands | |
| `categories.json` | GET - Categories | |
| `cross_references.json` | GET - CrossRef | |
| `days_in_transit.json` | GET - DaysInTransit | |
| `error_400.json` | Help - Errors | |
| `error_404_not_found.json` | GET - Products, GET - Inventory ("Not Found Response") | |
| `error_404_route.json` | Help - Errors | |
| `error_500.json` | Help - Errors | |
| `inventory.json` | GET - Inventory | |
| `orders.json` | GET - Orders | |
| `orders_cancel.json` | DELETE - Orders | |
| `orders_create.json` | POST - Orders (response) | `XX.XX` amounts replaced with numbers; the `XXXXXXXX-…` guid replaced with a nil UUID |
| `orders_create_request.json` | POST - Orders (request) | |
| `payment_profiles.json` | GET - Payment Profiles | |
| `products.json` | GET - Products | |
| `returns.json` | GET - Returns | |
| `returns_cancel.json` | DELETE - Returns | |
| `returns_create.json` | POST - Returns (response) | |
| `specs.json` | GET - Specs | |
| `styles.json` | GET - Styles | Raw line breaks inside the `description` string escaped as `\n` |
| `tracking.json` | GET - TrackingData | The unclosed outer list closed with `]` |
