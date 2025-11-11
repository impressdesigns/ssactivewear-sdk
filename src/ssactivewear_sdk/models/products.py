"""Product models."""

from datetime import datetime

from pydantic import Field

from ._base import SSActivewearBaseModel


class Warehouse(SSActivewearBaseModel):
    """Warehouse."""

    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Code identifying the Warehouse.",
    )
    sku_id: int = Field(
        alias="skuID",
        description="Unique ID for this sku (does not change)",
    )
    qty: int = Field(
        description="Quantity available for sale.",
    )
    closeout: bool = Field(
        description="Skus that are discontinued and will not be replenished.",
    )
    dropship: bool = Field(
        description="This product does not ship from our warehouse.",
    )
    exclude_free_freight: bool = Field(
        alias="excludeFreeFreight",
        description="This product does not qualify for free freight.",
    )
    full_case_only: bool = Field(
        alias="fullCaseOnly",
        description="This product must be ordered in full case quantities.",
    )
    returnable: bool = Field(
        description="This product is eligible for return.",
    )
    expected_inventory: str | None = Field(
        default=None,
        alias="expectedInventory",
        description=(
            "Current enroute quantities with expected dates of receipt and current quantity "
            "on order with the mill. If no dates are available, None will be returned."
        ),
    )


class Product(SSActivewearBaseModel):
    """Product."""

    sku_id_master: int = Field(
        alias="skuID_Master",
        description="Unique ID for this sku (does not change)",
    )
    sku: str = Field(
        description="Our sku number",
    )
    gtin: str = Field(
        description="Industry standard identifier used by all suppliers.",
    )
    your_sku: str = Field(
        alias="yourSku",
        description="YourSku has been set up using the CrossRef API.",
    )
    base_category_id: str = Field(
        alias="baseCategoryID",
        description="The base category ID for this product.",
    )
    brand_id: str = Field(
        alias="brandID",
        description="Unique ID for this brand (Will never change)",
    )
    brand_name: str = Field(
        alias="brandName",
        description="The brand that makes this style.",
    )
    style_id: int = Field(
        alias="styleID",
        description="Unique ID for this style (Will never change)",
    )
    style_name: str = Field(
        alias="styleName",
        description="The style's name. Style names are unique within a brand.",
    )
    color_name: str = Field(
        alias="colorName",
        description="The color of this product.",
    )
    color_code: str = Field(
        alias="colorCode",
        description="Two digit color code part of the InventoryKey.",
    )
    color_price_code_name: str = Field(
        alias="colorPriceCodeName",
        description="The pricing category of this color.",
    )
    color_group: str = Field(
        alias="colorGroup",
        description="Colors with a similar color group are considered to be a similar color.",
    )
    color_group_name: str = Field(
        alias="colorGroupName",
        description="Colors with a similar color group are considered to be a similar color.",
    )
    color_family_id: str = Field(
        alias="colorFamilyID",
        description="Base color the color falls under.",
    )
    color_family: str = Field(
        alias="colorFamily",
        description="Base color the color falls under.",
    )
    color_swatch_image: str = Field(
        alias="colorSwatchImage",
        description=(
            "URL to the medium swatch image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_swatch_text_color: str = Field(
        alias="colorSwatchTextColor",
        description="Html color code that is visible on top of the color swatch",
    )
    color_front_image: str = Field(
        alias="colorFrontImage",
        description=(
            "URL to the medium front image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_side_image: str = Field(
        alias="colorSideImage",
        description=(
            "URL to the medium side image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_back_image: str = Field(
        alias="colorBackImage",
        description=(
            "URL to the medium back image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_direct_side_image: str = Field(
        alias="colorDirectSideImage",
        description=(
            "URL to the medium direct side image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_on_model_front_image: str = Field(
        alias="colorOnModelFrontImage",
        description=(
            "URL to the medium on model front image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_on_model_side_image: str = Field(
        alias="colorOnModelSideImage",
        description=(
            "URL to the medium on model side image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color_on_model_back_image: str = Field(
        alias="colorOnModelBackImage",
        description=(
            "URL to the medium on model back image for this color - "
            "Example URL: https://www.ssactivewear.com/{Image} - "
            'Replace "_fm" with "_fl" for the large image - '
            'Replace "_fm" with "_fs" for the small image'
        ),
    )
    color1: str = Field(
        description="HTML Code for the primary color.",
    )
    color2: str = Field(
        description="HTML Code for the secondary color.",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size Name that the spec belongs to.",
    )
    size_code: str = Field(
        alias="sizeCode",
        description="One digit size code part of the InventoryKey.",
    )
    size_order: str = Field(
        alias="sizeOrder",
        description="Sort order for the size compared to other sizes in the style.",
    )
    size_price_code_name: str = Field(
        alias="sizePriceCodeName",
        description="The pricing category of this size.",
    )
    case_qty: int = Field(
        alias="caseQty",
        description="Number of units in a full case from the mill.",
    )
    unit_weight: float = Field(
        alias="unitWeight",
        description="Weight of a single unit.",
    )
    map_price: float = Field(
        alias="mapPrice",
        description="Minimum Advertised Price price",
    )
    piece_price: float = Field(
        alias="piecePrice",
        description="Piece price level price",
    )
    dozen_price: float = Field(
        alias="dozenPrice",
        description="Dozen price level price",
    )
    case_price: float = Field(
        alias="casePrice",
        description="Case price level price",
    )
    sale_price: float = Field(
        alias="salePrice",
        description="Sale price level price",
    )
    customer_price: float = Field(
        alias="customerPrice",
        description="Your price",
    )
    no_eretailing: bool = Field(
        alias="noeRetailing",
        description=(
            "When true, mill prohibits the selling of products on popular eRetailing "
            "platforms such as Amazon, Walmart, EBay."
        ),
    )
    case_weight: float = Field(
        alias="caseWeight",
        description="Weight of full case in pounds",
    )
    case_width: float = Field(
        alias="caseWidth",
        description="Width of case in inches",
    )
    case_length: float = Field(
        alias="caseLength",
        description="Length of case in inches",
    )
    case_height: float = Field(
        alias="caseHeight",
        description="Height of case in inches",
    )
    poly_pack_quantity: int = Field(
        alias="polyPackQty",
        description="Number of pieces in a poly pack",
    )
    quantity: int = Field(
        alias="qty",
        description="Combined Inventory in all of our warehouses",
    )
    country_of_origin: str = Field(
        alias="countryOfOrigin",
        description="Country of manufacture for product. Provided by mills.",
    )
    warehouses: list[Warehouse] = Field(
        description="List of Object",
    )
    sale_expiration: datetime | None = Field(
        default=None,
        alias="saleExpiration",
        description="Sale expiration date",
        strict=False,
    )
