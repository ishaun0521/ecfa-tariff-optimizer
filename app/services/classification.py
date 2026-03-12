from __future__ import annotations

from typing import Any

from app.schemas import AnalyzeRequest, OptimizeRequest
from app.services.rules import ECFA_SOURCES, PRODUCT_FAMILIES, get_case_context

CHINA_CUSTOMS_SOURCES = [
    {
        "name": "中華人民共和國海關總署官網",
        "url": "https://www.customs.gov.cn/",
        "jurisdiction": "CN",
        "use": "中國進口端海關制度、公告、預裁定與正式審核的官方入口。",
    },
    {
        "name": "中國海關線上辦事入口",
        "url": "https://online.customs.gov.cn/",
        "jurisdiction": "CN",
        "use": "中國海關線上申報 / 單一窗口 / 企業辦事入口。",
    },
    {
        "name": "中國政府網",
        "url": "https://www.gov.cn/",
        "jurisdiction": "CN",
        "use": "法規、部門規章與年度政策文件的中央政府入口。",
    },
]

CUSTOMS_BOUNDARY_NOTICE = (
    "本結果僅屬 pre-classification / precheck。最終稅則號列、進口稅率、ECFA 優惠適用與原產地接受與否，"
    "仍以中國海關接受申報、預裁定或正式審核結果為準。"
)


class _ReqView:
    product_name: str
    product_category: str | None
    current_hs_code: str | None
    product_description: str | None
    manufacturing_process: str | None
    packaging_form: str | None
    intended_use: str | None
    brand: str | None
    model: str | None
    net_weight: float | None
    retail_or_bulk: str | None
    supporting_documents: list[str]
    bom_items: list[Any]



def official_sources() -> dict[str, list[dict[str, str]]]:
    return {
        "taiwan": [
            *[
                {
                    "name": item["name"],
                    "url": item["url"],
                    "jurisdiction": "TW",
                    "use": item["use"],
                }
                for item in ECFA_SOURCES
            ],
            {
                "name": "財政部關務署－稅則稅率查詢及諮詢電話（官方入口）",
                "url": "https://web.customs.gov.tw/link/3078",
                "jurisdiction": "TW",
                "use": "台灣官方稅則 / 稅率查詢入口與諮詢入口。",
            },
            {
                "name": "財政部關務署－稅則稅率查詢系統入口",
                "url": "https://portal.sw.nat.gov.tw/APGQ/XGC411",
                "jurisdiction": "TW",
                "use": "台灣端稅則候選號列與稅率查詢系統入口。",
            },
        ],
        "china": CHINA_CUSTOMS_SOURCES,
    }



def _material_summary(req: _ReqView) -> tuple[list[str], list[str]]:
    item_names = [item.material_name for item in req.bom_items]
    non_tw = [item.material_name for item in req.bom_items if (item.origin_country or '').upper() not in ('TW', 'TAIWAN')]
    return item_names, non_tw



def _missing_facts(req: _ReqView) -> list[str]:
    missing = []
    if not req.product_description:
        missing.append("product_description")
    if not req.manufacturing_process:
        missing.append("manufacturing_process")
    if not req.packaging_form:
        missing.append("packaging_form")
    if not req.intended_use:
        missing.append("intended_use")
    if not req.bom_items:
        missing.append("bom_items")
    if not req.supporting_documents:
        missing.append("supporting_documents")
    return missing



def classify_product(req: AnalyzeRequest | OptimizeRequest) -> dict[str, Any]:
    case_context = get_case_context(req.product_name, req.product_category, req.bom_items)
    family_rule = PRODUCT_FAMILIES[case_context["family"]]
    template = case_context.get("template")
    item_names, non_tw_materials = _material_summary(req)
    missing_facts = _missing_facts(req)

    candidate_codes = []
    seen = []
    base_candidates = []
    if req.current_hs_code:
        base_candidates.append(req.current_hs_code)
    if template:
        base_candidates.extend(template.get("candidate_hs_codes", []))
    base_candidates.extend(family_rule.get("candidate_hs_codes", []))

    for idx, code in enumerate(base_candidates):
        if not code or code in seen:
            continue
        seen.append(code)
        confidence = "high" if req.current_hs_code and code == req.current_hs_code else ("medium" if idx == 0 else "low")
        why_fit = []
        if template:
            why_fit.append(f"商品命中「{template['display_name']}」案例模板。")
            if case_context["matched_key_materials"]:
                why_fit.append(f"已辨識關鍵材料：{', '.join(case_context['matched_key_materials'][:4])}。")
        if req.packaging_form:
            why_fit.append(f"目前包裝型態為「{req.packaging_form}」，會影響成品 / 原料 / 零售型態歸類。")
        if req.intended_use:
            why_fit.append(f"商品用途描述為「{req.intended_use}」。")

        why_not = []
        if missing_facts:
            why_not.append("關鍵商品事實尚未補齊，候選號列仍需人工覆核。")
        if non_tw_materials:
            why_not.append(f"非台灣來源材料包含：{', '.join(non_tw_materials[:4])}，後續原產地判定仍需獨立檢查。")

        candidate_codes.append(
            {
                "code": code,
                "confidence": confidence,
                "basis_summary": f"依商品名稱、案例模板與目前已知商品事實，先列為候選號列 {code}。",
                "why_it_may_fit": why_fit,
                "why_it_may_not_fit": why_not,
                "missing_facts": list(missing_facts),
                "risk_level": "medium" if missing_facts else "low",
            }
        )

    if not candidate_codes:
        classification_status = "insufficient_data"
        selected_working_hs_code = None
    elif missing_facts:
        classification_status = "needs_manual_review"
        selected_working_hs_code = req.current_hs_code or candidate_codes[0]["code"]
    else:
        classification_status = "preliminary"
        selected_working_hs_code = req.current_hs_code or candidate_codes[0]["code"]

    basis_parts = [
        f"商品名稱：{req.product_name}",
        f"案例模板：{case_context['case_name'] or '未命中模板'}",
        f"商品家族：{family_rule['label']}",
    ]
    if req.product_description:
        basis_parts.append(f"商品描述：{req.product_description}")
    if req.manufacturing_process:
        basis_parts.append(f"製程：{req.manufacturing_process}")
    if req.packaging_form:
        basis_parts.append(f"包裝型態：{req.packaging_form}")
    if item_names:
        basis_parts.append(f"主要材料：{', '.join(item_names[:5])}")

    warnings = []
    if missing_facts:
        warnings.append("商品事實欄位未補齊，當前結果僅能作為前期候選判定。")
    if len(candidate_codes) > 1:
        warnings.append("目前存在多個候選號列，建議以報關型態、成分比例與包裝方式再做人工覆核。")
    if template and template.get("common_risks"):
        warnings.extend(template["common_risks"][:2])

    recommended_next_checks = list(case_context.get("recommended_next_checks", []))
    recommended_next_checks.extend([
        "用官方稅則查詢入口核對候選號列與章節說明。",
        "與中國進口端報關行 / 關務顧問確認最終申報邏輯。",
    ])

    manual_review_triggers = []
    if len(candidate_codes) > 1:
        manual_review_triggers.append("候選號列超過 1 個")
    if missing_facts:
        manual_review_triggers.append("關鍵商品事實不足")
    if req.retail_or_bulk:
        manual_review_triggers.append("零售 / 散裝型態需與實際進口報關一致")
    if non_tw_materials:
        manual_review_triggers.append("原料來源複雜，稅則與原產地需分開覆核")

    return {
        "candidate_hs_codes": candidate_codes,
        "selected_working_hs_code": selected_working_hs_code,
        "classification_status": classification_status,
        "classification_basis_summary": "；".join(basis_parts),
        "key_missing_facts": missing_facts,
        "warnings": warnings,
        "recommended_next_checks": recommended_next_checks,
        "manual_review_triggers": manual_review_triggers,
        "customs_boundary_notice": CUSTOMS_BOUNDARY_NOTICE,
        "official_sources": official_sources(),
    }
