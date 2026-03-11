from app.schemas import AnalyzeRequest

def analyze_product(req: AnalyzeRequest):
    total_ratio = round(sum(item.ratio for item in req.bom_items), 4)
    adjustable_count = sum(1 for item in req.bom_items if item.adjustable)
    top_materials = sorted(req.bom_items, key=lambda x: x.ratio, reverse=True)[:5]
    return {
        "product_name": req.product_name,
        "destination_country": req.destination_country,
        "current_hs_code": req.current_hs_code,
        "current_tariff_rate": req.current_tariff_rate,
        "summary": {
            "bom_item_count": len(req.bom_items),
            "total_ratio": total_ratio,
            "adjustable_item_count": adjustable_count,
            "ratio_warning": total_ratio != 100,
        },
        "top_materials": [
            {
                "material_name": item.material_name,
                "ratio": item.ratio,
                "origin_country": item.origin_country,
            }
            for item in top_materials
        ],
        "mock_ecfa_result": {
            "status": "needs_rule_check",
            "message": "MVP 版本尚未接入正式 ECFA 規則表，先回傳分析摘要。"
        }
    }
