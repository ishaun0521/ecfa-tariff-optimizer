from typing import List, Optional
from pydantic import BaseModel, Field

class BomItem(BaseModel):
    material_name: str
    ratio: float = Field(..., ge=0, le=100)
    cost: float = Field(..., ge=0)
    origin_country: str
    adjustable: bool = True

class Constraints(BaseModel):
    max_cost_increase_pct: float = 0.0
    locked_materials: List[str] = []
    notes: Optional[str] = None

class AnalyzeRequest(BaseModel):
    product_name: str
    destination_country: str = "CN"
    current_hs_code: Optional[str] = None
    current_tariff_rate: Optional[float] = None
    bom_items: List[BomItem]

class OptimizeRequest(BaseModel):
    product_name: str
    destination_country: str = "CN"
    current_hs_code: Optional[str] = None
    current_tariff_rate: float
    bom_items: List[BomItem]
    constraints: Constraints
