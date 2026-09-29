"""Catalog models: categories, brands, styles, products, inventory, and specs."""

from decimal import Decimal

from pydantic import AliasChoices, Field

from ._base import FlexibleDatetime, FlexibleStr, OptionalFlexibleInt, SSActivewearBaseModel


class Category(SSActivewearBaseModel):
    """A category that styles are assigned to."""

    category_id: int = Field(
        alias="categoryID",
        description="Unique ID for this category (does not change).",
    )
    name: str = Field(
        description="Logical name for the category.",
    )
    image: str | None = Field(
        default=None,
        description="Deprecated by S&S.",
    )


class Brand(SSActivewearBaseModel):
    """A brand that styles are assigned to."""

    brand_id: int = Field(
        alias="brandID",
        description="Unique ID for this brand (does not change).",
    )
    name: str = Field(
        description="Logical name for the brand.",
    )
    image: str = Field(
        description=(
            "URL to the image for this brand. Alternate image sizes are available: "
            "_fl is large, _fm is medium and _fs is small."
        ),
    )
    no_eretailing: bool = Field(
        alias="noeRetailing",
        description=(
            "When true, mill prohibits the selling of products on popular eRetailing "
            "platforms such as Amazon, Walmart, EBay."
        ),
    )


class MediaAsset(SSActivewearBaseModel):
    """An image of a style or product."""

    image: str = Field(
        description="URL to the image.",
    )
    asset_type: str = Field(
        # Styles send ``assetType``, products send ``asset_type``.
        validation_alias=AliasChoices("asset_type", "assetType"),
        serialization_alias="asset_type",
        description="Type of image, e.g. Style, Front, Back, DirectSide, OnModel_Front.",
    )


class Style(SSActivewearBaseModel):
    """Style level information that is repeated on every sku within the style."""

    style_id: int = Field(
        alias="styleID",
        description="Unique ID for this style (does not change).",
    )
    part_number: str = Field(
        alias="partNumber",
        description="First 5 digits of our sku number. It is the same for all skus in the style.",
    )
    brand_name: str = Field(
        alias="brandName",
        description="The brand that makes this style.",
    )
    style_name: str = Field(
        alias="styleName",
        description="The style's name. Style names are unique within a brand.",
    )
    title: str = Field(
        description="A short description of the style.",
    )
    description: str = Field(
        description="Long HTML description of the style.",
    )
    base_category: str = Field(
        # The object definition misspells this as ``baseCateogry``.
        validation_alias=AliasChoices("baseCategory", "baseCateogry"),
        serialization_alias="baseCategory",
        description="Primary category for the style. Only one per style.",
    )
    categories: str = Field(
        description="Comma separated list of category IDs that the style belongs to.",
    )
    catalog_page_number: FlexibleStr = Field(
        alias="catalogPageNumber",
        description="Page number the style appears in our current catalog.",
    )
    new_style: bool = Field(
        alias="newStyle",
        description="Defines if the style is new.",
    )
    comparable_group: OptionalFlexibleInt = Field(
        default=None,
        alias="comparableGroup",
        description="Styles with the same comparable group are considered to be similar products.",
    )
    companion_group: OptionalFlexibleInt = Field(
        default=None,
        alias="companionGroup",
        description="Styles with the same companion group are considered to be within the same product family.",
    )
    brand_image: str = Field(
        alias="brandImage",
        description="URL to the medium image for this style's brand.",
    )
    style_image: str = Field(
        alias="styleImage",
        description="URL to the medium image for this style.",
    )
    sustainable_style: bool | None = Field(
        default=None,
        alias="sustainableStyle",
        description=(
            "Defines if the style meets S&S Sustainable Materials, Manufacturing, "
            "& Socially Conscious Manufacturing criteria."
        ),
    )
    media_assets: list[MediaAsset] = Field(
        default_factory=list,
        alias="mediaAssets",
        description="Images of the style.",
    )

    @property
    def category_ids(self) -> list[int]:
        """The IDs in :attr:`categories`, parsed."""
        return [int(category) for category in self.categories.split(",") if category.strip()]


class ProductWarehouse(SSActivewearBaseModel):
    """A product's stock in one warehouse."""

    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Code identifying the warehouse.",
    )
    sku_id: int = Field(
        alias="skuID",
        description="ID identifying the sku and warehouse.",
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
            "on order with the mill, e.g. ``EnRoute:None|OnOrder:None``."
        ),
    )


class Product(SSActivewearBaseModel):
    """A sku, with pricing and per-warehouse stock."""

    sku: str = Field(
        description="Our sku number.",
    )
    gtin: str = Field(
        description="Industry standard identifier used by all suppliers.",
    )
    sku_id_master: int = Field(
        alias="skuID_Master",
        description="Unique ID for this sku (does not change).",
    )
    your_sku: str = Field(
        alias="yourSku",
        description="Your sku, set up using the cross reference API.",
    )
    style_id: int = Field(
        alias="styleID",
        description="Unique ID for this style (does not change).",
    )
    brand_name: str = Field(
        alias="brandName",
        description="The brand that makes this style.",
    )
    brand_id: FlexibleStr = Field(
        alias="brandID",
        description="Unique ID for this brand (does not change).",
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
    color_group: FlexibleStr = Field(
        alias="colorGroup",
        description="Colors with a similar color group are considered to be a similar color.",
    )
    color_group_name: str = Field(
        alias="colorGroupName",
        description="Colors with a similar color group are considered to be a similar color.",
    )
    color_family_id: FlexibleStr = Field(
        alias="colorFamilyID",
        description="Base color the color falls under.",
    )
    color_family: str = Field(
        alias="colorFamily",
        description="Base color the color falls under.",
    )
    base_category_id: FlexibleStr = Field(
        alias="baseCategoryID",
        description="The base category ID for this product.",
    )
    color_swatch_image: str = Field(
        alias="colorSwatchImage",
        description='URL to the medium swatch image for this color. Replace "_fm" with "_fs" for the small image.',
    )
    color_swatch_text_color: str = Field(
        alias="colorSwatchTextColor",
        description="HTML color code that is visible on top of the color swatch.",
    )
    color_front_image: str = Field(
        alias="colorFrontImage",
        description="URL to the medium front image for this color.",
    )
    color_side_image: str = Field(
        alias="colorSideImage",
        description="URL to the medium side image for this color.",
    )
    color_back_image: str = Field(
        alias="colorBackImage",
        description="URL to the medium back image for this color.",
    )
    color_direct_side_image: str = Field(
        alias="colorDirectSideImage",
        description="URL to the medium direct side image for this color.",
    )
    color_on_model_front_image: str = Field(
        alias="colorOnModelFrontImage",
        description="URL to the medium on model front image for this color.",
    )
    color_on_model_side_image: str = Field(
        alias="colorOnModelSideImage",
        description="URL to the medium on model side image for this color.",
    )
    color_on_model_back_image: str = Field(
        alias="colorOnModelBackImage",
        description="URL to the medium on model back image for this color.",
    )
    color1: str = Field(
        description="HTML code for the primary color.",
    )
    color2: str = Field(
        description="HTML code for the secondary color.",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size name.",
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
    unit_weight: Decimal = Field(
        alias="unitWeight",
        description="Weight of a single unit.",
    )
    map_price: Decimal = Field(
        alias="mapPrice",
        description="Minimum advertised price.",
    )
    retail_price: Decimal | None = Field(
        default=None,
        alias="retailPrice",
        description="Manufacturer's suggested retail price.",
    )
    piece_price: Decimal = Field(
        alias="piecePrice",
        description="Piece price level price.",
    )
    dozen_price: Decimal = Field(
        alias="dozenPrice",
        description="Dozen price level price.",
    )
    case_price: Decimal = Field(
        alias="casePrice",
        description="Case price level price.",
    )
    sale_price: Decimal = Field(
        alias="salePrice",
        description="Sale price level price.",
    )
    customer_price: Decimal = Field(
        alias="customerPrice",
        description="Your price.",
    )
    sale_expiration: FlexibleDatetime = Field(
        default=None,
        alias="saleExpiration",
        description="When the sale price expires.",
    )
    no_eretailing: bool = Field(
        alias="noeRetailing",
        description=(
            "When true, mill prohibits the selling of products on popular eRetailing "
            "platforms such as Amazon, Walmart, EBay."
        ),
    )
    case_weight: Decimal = Field(
        alias="caseWeight",
        description="Weight of full case in pounds.",
    )
    case_width: Decimal = Field(
        alias="caseWidth",
        description="Width of case in inches.",
    )
    case_length: Decimal = Field(
        alias="caseLength",
        description="Length of case in inches.",
    )
    case_height: Decimal = Field(
        alias="caseHeight",
        description="Height of case in inches.",
    )
    poly_pack_qty: int = Field(
        # The object definition capitalizes this as ``PolyPackQty``.
        validation_alias=AliasChoices("polyPackQty", "PolyPackQty"),
        serialization_alias="polyPackQty",
        description="Number of pieces in a poly pack.",
    )
    qty: int = Field(
        description="Combined inventory in all of our warehouses.",
    )
    country_of_origin: str = Field(
        alias="countryOfOrigin",
        description="Country of manufacture for product. Provided by mills.",
    )
    warehouses: list[ProductWarehouse] = Field(
        default_factory=list,
        description="Stock in each warehouse.",
    )
    media_assets: list[MediaAsset] = Field(
        default_factory=list,
        alias="mediaAssets",
        description="Images of the product.",
    )


class InventoryWarehouse(SSActivewearBaseModel):
    """A sku's stock in one warehouse."""

    warehouse_abbr: str = Field(
        alias="warehouseAbbr",
        description="Code identifying the warehouse.",
    )
    sku_id: int = Field(
        alias="skuID",
        description="ID identifying the sku and warehouse.",
    )
    qty: int = Field(
        description="Quantity available for sale.",
    )


class InventoryItem(SSActivewearBaseModel):
    """Warehouse inventory for a sku, without the rest of the product payload."""

    sku: str = Field(
        description="Our sku number.",
    )
    gtin: str = Field(
        description="Industry standard identifier used by all suppliers.",
    )
    sku_id_master: int = Field(
        # The object definition calls this ``skuID``; the payload sends ``skuID_Master``.
        validation_alias=AliasChoices("skuID_Master", "skuID"),
        serialization_alias="skuID_Master",
        description="Unique ID for this sku (does not change).",
    )
    your_sku: str = Field(
        alias="yourSku",
        description="Your sku, set up using the cross reference API.",
    )
    style_id: int = Field(
        alias="styleID",
        description="Unique ID for this style (does not change).",
    )
    warehouses: list[InventoryWarehouse] = Field(
        default_factory=list,
        description="Stock in each warehouse.",
    )


class Spec(SSActivewearBaseModel):
    """One line of a style's spec sheet."""

    spec_id: int = Field(
        alias="specID",
        description="Unique ID for this spec (does not change).",
    )
    style_id: int = Field(
        alias="styleID",
        description="Unique ID for this style (does not change).",
    )
    part_number: str = Field(
        alias="partNumber",
        description="First 5 digits of our sku number. It is the same for all skus in the style.",
    )
    brand_name: str = Field(
        alias="brandName",
        description="The brand that makes this style.",
    )
    style_name: str = Field(
        alias="styleName",
        description="The style's name. Style names are unique within a brand.",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size name that the spec belongs to.",
    )
    size_order: str = Field(
        alias="sizeOrder",
        description="Sort order for the size compared to other sizes in the style.",
    )
    spec_name: str = Field(
        alias="specName",
        description="The name of the spec.",
    )
    value: str = Field(
        description="The value of the spec.",
    )
