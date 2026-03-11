from app.schemas import OptimizeRequest

def optimize_bom(req: OptimizeRequest):
    adjustable = [i for i in req.bom_items if i.adjustable and i.material_name not in req.constraints.locked_materials]
    adjustable = sorted(adjustable, key=lambda x: x.ratio, reverse=True)

    scenarios = []
    for idx, item in enumerate(adjustable[:3], start=1):
        reduction = round(min(2.0, max(0.5, item.ratio * 0.05)), 2)
        cost_increase = round(min(req.constraints.max_cost_increase_pct or 2.0, max(0.2, item.cost * 0.01)), 2)
        new_rate = round(max(0, req.current_tariff_rate - reduction), 2)
        scenarios.append({
            "scenario_name": f"方案 {idx}",
            "bom_changes": [
                {
                    "material_name": item.material_name,
                    "suggested_change": f"調整 {item.material_name} 比例或改用更有利來源",
                    "current_ratio": item.ratio,
                    "suggested_ratio": round(item.ratio + 2, 2),
                    "origin_country": item.origin_country,
                }
            ],
            "estimated_new_tariff_rate": new_rate,
            "tariff_reduction_pct": reduction,
            "estimated_cost_increase_pct": cost_increase,
            "risk_level": "medium" if idx == 1 else "low",
            "summary": f"優先檢查 {item.material_name}，以小幅 BOM 調整換取較高的潛在降稅空間。"
        })

    return {
        "product_name": req.product_name,
        "current_tariff_rate": req.current_tariff_rate,
        "constraints": req.constraints.model_dump(),
        "candidate_scenarios": scenarios,
        "note": "這是 MVP mock optimizer，後續可接入正式 ECFA 規則、成本模型與數學最佳化。"
    }
