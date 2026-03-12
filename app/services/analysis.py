from app.schemas import AnalyzeRequest
from app.services.classification import classify_product
from app.services.explainer import build_analysis_explanation
from app.services.rules import build_origin_breakdown, evaluate_ecfa_precheck, get_case_context

FOOD_KEYWORDS = ["food", "食品", "drink", "beverage", "snack", "tea", "sauce", "noodle", "dessert"]


def _detect_missing_fields(req: AnalyzeRequest, total_ratio: float) -> list[str]:
    missing_fields = []

    if not req.current_hs_code:
        missing_fields.append("current_hs_code")
    if req.current_tariff_rate is None:
        missing_fields.append("current_tariff_rate")
    if not req.declared_origin_country:
        missing_fields.append("declared_origin_country")
    if total_ratio != 100:
        missing_fields.append("bom_items.ratio_total")

    for index, item in enumerate(req.bom_items):
        if not item.hs_code:
            missing_fields.append(f"bom_items[{index}].hs_code")
        if not item.supplier_name:
            missing_fields.append(f"bom_items[{index}].supplier_name")

    return missing_fields


def _build_warnings(req: AnalyzeRequest, total_ratio: float, origin_country_count: int) -> list[str]:
    warnings = []
    if total_ratio != 100:
        warnings.append(f"BOM ratio total is {total_ratio}, not 100. Please verify formulation percentages.")
    if req.current_tariff_rate is None:
        warnings.append("Current tariff rate is missing, so downstream savings are only directional.")
    if origin_country_count <= 1:
        warnings.append("Only one origin country appears in the BOM; origin qualification may still need document review.")

    product_text = f"{req.product_name} {req.product_category or ''}".lower()
    if any(keyword in product_text for keyword in FOOD_KEYWORDS):
        warnings.append("Food products often require ingredient-origin, process, and sanitary document checks beyond BOM percentage review.")

    return warnings


def analyze_product(req: AnalyzeRequest):
    total_ratio = round(sum(item.ratio for item in req.bom_items), 4)
    adjustable_count = sum(1 for item in req.bom_items if item.adjustable)
    top_materials = sorted(req.bom_items, key=lambda x: x.ratio, reverse=True)[:5]

    tariff_classification = classify_product(req)
    origin_breakdown, origin_ratio, _, total_cost = build_origin_breakdown(req.bom_items)
    dominant_origin = origin_breakdown[0]["origin_country"] if origin_breakdown else None
    case_context = get_case_context(req.product_name, req.product_category, req.bom_items)
    ecfa_precheck = evaluate_ecfa_precheck(
        product_name=req.product_name,
        product_category=req.product_category,
        current_hs_code=req.current_hs_code or tariff_classification.get("selected_working_hs_code"),
        destination_country=req.destination_country,
        declared_origin_country=req.declared_origin_country,
        bom_items=req.bom_items,
    )

    missing_fields = _detect_missing_fields(req, total_ratio)
    warnings = _build_warnings(req, total_ratio, len(origin_ratio))
    warnings.extend([w for w in ecfa_precheck["warnings"] if w not in warnings])
    warnings.extend([w for w in tariff_classification["warnings"] if w not in warnings])
    for field in ecfa_precheck["missing_fields"]:
        if field not in missing_fields:
            missing_fields.append(field)
    for field in tariff_classification["key_missing_facts"]:
        if field not in missing_fields:
            missing_fields.append(field)

    scenario_score = max(
        0,
        min(
            100,
            round(
                ecfa_precheck["origin_metrics"]["taiwan_ratio_pct"] * 0.75
                + adjustable_count * 4
                + len(case_context["matched_key_materials"]) * 3
                - len(warnings) * 5
                - len(missing_fields) * 2
            ),
        ),
    )

    ai_explanation = build_analysis_explanation(
        product_name=req.product_name,
        summary={
            "detected_product_case": case_context["case_name"],
            "selected_working_hs_code": tariff_classification.get("selected_working_hs_code"),
        },
        tariff_classification=tariff_classification,
        ecfa_precheck=ecfa_precheck,
        case_insights=case_context["case_insights"],
        key_risk_materials=case_context["key_risk_materials"],
        recommended_next_checks=case_context["recommended_next_checks"],
    )

    return {
        "product_name": req.product_name,
        "destination_country": req.destination_country,
        "product_category": req.product_category,
        "current_hs_code": req.current_hs_code,
        "current_tariff_rate": req.current_tariff_rate,
        "declared_origin_country": req.declared_origin_country,
        "summary": {
            "bom_item_count": len(req.bom_items),
            "total_ratio": total_ratio,
            "adjustable_item_count": adjustable_count,
            "total_cost": total_cost,
            "ratio_warning": total_ratio != 100,
            "dominant_origin_country": dominant_origin,
            "detected_product_case": case_context["case_name"],
            "selected_working_hs_code": tariff_classification.get("selected_working_hs_code"),
        },
        "origin_breakdown": origin_breakdown,
        "top_materials": [
            {
                "material_name": item.material_name,
                "ratio": item.ratio,
                "origin_country": item.origin_country,
                "adjustable": item.adjustable,
                "hs_code": item.hs_code,
                "supplier_name": item.supplier_name,
            }
            for item in top_materials
        ],
        "warnings": warnings,
        "missing_fields": missing_fields,
        "scenario_score": scenario_score,
        "ai_explanation": ai_explanation,
        "tariff_classification": tariff_classification,
        "ecfa_precheck": ecfa_precheck,
        "case_insights": case_context["case_insights"],
        "key_risk_materials": case_context["key_risk_materials"],
        "recommended_next_checks": case_context["recommended_next_checks"],
        "customs_boundary_notice": tariff_classification["customs_boundary_notice"],
        "commercial_assessment": {
            "stage": "precheck",
            "status": ecfa_precheck["origin_precheck_status"],
            "case_name": case_context["case_name"],
            "focus": case_context["commercial_focus"],
            "priority_levers": case_context["priority_levers"],
            "message": "此結果可作為商業前期判斷與案件分流，正式享惠仍需依實際稅則號列、原產地文件與報關審核確認。",
        },
    }
