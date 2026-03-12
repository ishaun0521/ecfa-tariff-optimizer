from app.schemas import OptimizeRequest
from app.services.rules import evaluate_ecfa_precheck, get_case_context


def optimize_bom(req: OptimizeRequest):
    locked = set(req.constraints.locked_materials)
    adjustable = [i for i in req.bom_items if i.adjustable and i.material_name not in locked]
    total_ratio = round(sum(item.ratio for item in req.bom_items), 4)
    missing_fields = []
    warnings = []
    if total_ratio != 100:
        missing_fields.append("bom_items.ratio_total")
        warnings.append(f"BOM ratio total is {total_ratio}, not 100.")
    if not req.current_hs_code:
        missing_fields.append("current_hs_code")
    if not req.declared_origin_country:
        missing_fields.append("declared_origin_country")
    if not adjustable:
        warnings.append("No adjustable BOM items available after locked-material filtering.")

    case_context = get_case_context(req.product_name, req.product_category, req.bom_items)
    priority_levers = case_context["priority_levers"]

    def priority_key(item):
        lever_rank = next((idx for idx, lever in enumerate(priority_levers) if lever.lower() in item.material_name.lower()), len(priority_levers) + 1)
        non_tw_bonus = 0 if item.origin_country != "TW" else 1
        return (lever_rank, non_tw_bonus, -item.ratio, -item.cost)

    adjustable = sorted(adjustable, key=priority_key)

    ecfa_precheck = evaluate_ecfa_precheck(
        product_name=req.product_name,
        product_category=req.product_category,
        current_hs_code=req.current_hs_code,
        destination_country=req.destination_country,
        declared_origin_country=req.declared_origin_country,
        bom_items=req.bom_items,
    )
    warnings.extend([w for w in ecfa_precheck["warnings"] if w not in warnings])
    for field in ecfa_precheck["missing_fields"]:
        if field not in missing_fields:
            missing_fields.append(field)

    tw_ratio = ecfa_precheck["origin_metrics"]["taiwan_ratio_pct"]
    target_origin_ratio = req.constraints.target_origin_ratio or max(60.0, tw_ratio)
    ratio_gap = max(0.0, round(target_origin_ratio - tw_ratio, 2))
    scenario_limit = req.constraints.max_material_adjustment_count or 3
    scenario_inputs = adjustable[: min(3, scenario_limit)]
    scenarios = []

    for idx, item in enumerate(scenario_inputs, start=1):
        matched_priority = next((lever for lever in priority_levers if lever.lower() in item.material_name.lower()), None)
        is_priority_material = matched_priority is not None
        increase = round(min(6.0, max(1.2, ratio_gap if ratio_gap else item.ratio * 0.08)), 2)
        if item.origin_country == "TW":
            suggested_origin = "TW"
            change_text = f"維持 {item.material_name} 為台灣來源，優先提高其 BOM 占比或在台加工比重"
            expected_ratio_delta = increase
        else:
            suggested_origin = "TW"
            change_text = f"評估將 {item.material_name} 改為台灣來源或在台完成關鍵製程"
            expected_ratio_delta = increase

        cost_ceiling = req.constraints.max_cost_increase_pct or 3.0
        cost_increase = round(min(cost_ceiling, max(0.4, item.cost * 0.01)), 2)
        legal_strength = 74 if is_priority_material else 66
        if item.origin_country == "TW":
            legal_strength -= 6
        feasibility = max(0, min(100, round(legal_strength + item.ratio * 0.3 - cost_increase * 8 - len(locked) * 2)))
        estimated_tariff_reduction = round(min(req.current_tariff_rate, max(0.6, increase * 0.22 + (0.35 if is_priority_material else 0))), 2)
        new_rate = round(max(0, req.current_tariff_rate - estimated_tariff_reduction), 2)
        scenario_score = max(0, min(100, round(feasibility * 0.55 + estimated_tariff_reduction * 18 - cost_increase * 5 + (4 if is_priority_material else 0))))

        case_summary_prefix = case_context["case_name"] or req.product_name
        scenario_name = f"方案 {idx}｜{item.material_name}"
        scenario_warnings = [
            f"{item.material_name} 的調整屬商業最佳化建議，正式享惠前仍需核對供應商、原料來源與證明文件。"
        ]
        if case_context["common_risks"]:
            scenario_warnings.append(case_context["common_risks"][0])

        case_insight = case_context["case_insights"][1] if len(case_context["case_insights"]) > 1 else ""
        next_checks = list(case_context["recommended_next_checks"])
        if matched_priority:
            next_checks.insert(0, f"優先確認 {matched_priority} 的替代供應商、在台加工與單價影響。")

        scenarios.append(
            {
                "scenario_name": scenario_name,
                "scenario_score": scenario_score,
                "feasibility_score": feasibility,
                "legal_basis_summary": [
                    "需先確認成品最終報關號列是否位於 ECFA 原產地貨品清單內",
                    "需依 ECFA 原產地認定基準確認台灣來源、台灣製程與附加價值是否足夠",
                    "需備妥 ECFA 統一規章所需之原產地證明與佐證文件",
                ],
                "warnings": scenario_warnings,
                "bom_changes": [
                    {
                        "material_name": item.material_name,
                        "suggested_change": change_text,
                        "current_ratio": item.ratio,
                        "suggested_ratio": round(item.ratio + expected_ratio_delta, 2),
                        "origin_country": item.origin_country,
                        "suggested_origin_country": suggested_origin,
                    }
                ],
                "estimated_new_tariff_rate": new_rate,
                "tariff_reduction_pct": estimated_tariff_reduction,
                "estimated_cost_increase_pct": cost_increase,
                "risk_level": "medium" if item.origin_country != "TW" else "low",
                "key_risk_materials": case_context["key_risk_materials"],
                "recommended_next_checks": next_checks,
                "case_insights": [entry for entry in [case_insight, f"此方案優先鎖定 {case_summary_prefix} 案件中的 {item.material_name}。"] if entry],
                "summary": f"以 {item.material_name} 作為優先槓桿，處理 {case_summary_prefix} 的關鍵卡點，目標把台灣來源比重往 {target_origin_ratio}% 靠近。",
            }
        )

    ranked_scenarios = sorted(scenarios, key=lambda s: s["scenario_score"], reverse=True)
    recommended = ranked_scenarios[0] if ranked_scenarios else None

    return {
        "product_name": req.product_name,
        "product_category": req.product_category,
        "destination_country": req.destination_country,
        "current_hs_code": req.current_hs_code,
        "declared_origin_country": req.declared_origin_country,
        "current_tariff_rate": req.current_tariff_rate,
        "constraints": req.constraints.model_dump(),
        "warnings": warnings,
        "missing_fields": missing_fields,
        "ecfa_precheck": ecfa_precheck,
        "case_insights": case_context["case_insights"],
        "key_risk_materials": case_context["key_risk_materials"],
        "recommended_next_checks": case_context["recommended_next_checks"],
        "summary": {
            "bom_item_count": len(req.bom_items),
            "adjustable_candidate_count": len(adjustable),
            "locked_material_count": len(locked),
            "generated_scenario_count": len(ranked_scenarios),
            "target_origin_ratio_pct": target_origin_ratio,
            "current_taiwan_ratio_pct": tw_ratio,
            "origin_ratio_gap_pct": ratio_gap,
            "detected_product_case": case_context["case_name"],
        },
        "commercial_assessment": {
            "stage": "optimization",
            "status": "scenario_generated" if ranked_scenarios else "insufficient_inputs",
            "case_name": case_context["case_name"],
            "focus": case_context["commercial_focus"],
            "priority_levers": case_context["priority_levers"],
            "message": "以下方案是商業最佳化建議，不等於已取得 ECFA 資格；仍須先通過 legal precheck 與文件審核。",
        },
        "recommended_scenario": recommended,
        "candidate_scenarios": ranked_scenarios,
        "commercial_note": "本結果將 ECFA 法規前置條件與 BOM 商業最佳化分開呈現：是否享惠仍需先過貨品清單、原產地基準與文件三關。",
    }
