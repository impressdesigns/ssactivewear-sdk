"""Cross reference models."""

from pydantic import Field

from ._base import SSActivewearBaseModel


class CrossReference(SSActivewearBaseModel):
    """A sku mapped to your own sku."""

    your_sku: str = Field(
        alias="yourSku",
        description="Your sku number.",
    )
    sku_id: int = Field(
        alias="skuID",
        description="Unique ID for this sku (does not change).",
    )
    sku: str = Field(
        description="Our sku number.",
    )
    gtin: str = Field(
        description="Industry standard identifier used by all suppliers.",
    )
    brand_name: str = Field(
        alias="brandName",
        description="The brand that makes this style.",
    )
    style_name: str = Field(
        alias="styleName",
        description="The style's name. Style names are unique within a brand.",
    )
    color_name: str = Field(
        alias="colorName",
        description="The color of this product.",
    )
    size_name: str = Field(
        alias="sizeName",
        description="Size name.",
    )
