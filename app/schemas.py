from typing import List, Optional
from pydantic import BaseModel, Field


class BomItem(BaseModel):
    material_name: str
    ratio: float = Field(..., ge=0, le=100)
    cost: float = Field(..., ge=0)
    origin_country: str
    adjustable: bool = True
    hs_code: Optional[str] = None
    supplier_name: Optional[str] = None
    notes: Optional[str] = None


class Constraints(BaseModel):
    max_cost_increase_pct: float = 0.0
    locked_materials: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    target_origin_ratio: Optional[float] = Field(default=None, ge=0, le=100)
    max_material_adjustment_count: Optional[int] = Field(default=None, ge=1)


class ProductFactsMixin(BaseModel):
    product_description: Optional[str] = None
    manufacturing_process: Optional[str] = None
    packaging_form: Optional[str] = None
    intended_use: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    net_weight: Optional[float] = Field(default=None, ge=0)
    retail_or_bulk: Optional[str] = None
    supporting_documents: List[str] = Field(default_factory=list)


class AnalyzeRequest(ProductFactsMixin):
    product_name: str
    destination_country: str = "CN"
    current_hs_code: Optional[str] = None
    current_tariff_rate: Optional[float] = Field(default=None, ge=0)
    declared_origin_country: Optional[str] = None
    product_category: Optional[str] = None
    bom_items: List[BomItem]


class OptimizeRequest(ProductFactsMixin):
    product_name: str
    destination_country: str = "CN"
    current_hs_code: Optional[str] = None
    current_tariff_rate: float = Field(..., ge=0)
    declared_origin_country: Optional[str] = None
    product_category: Optional[str] = None
    bom_items: List[BomItem]
    constraints: Constraints = Field(default_factory=Constraints)
