from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.schemas import BomItem

ECFA_SOURCES = [
    {
        "name": "財政部關務署－原產地規則總頁",
        "url": "https://web.customs.gov.tw/singlehtml/715",
        "use": "ECFA 原產地文件官方入口",
    },
    {
        "name": "ECFA 原產地認定基準",
        "url": "https://web.customs.gov.tw/download/m232104",
        "use": "原產地認定規則與基準",
    },
    {
        "name": "ECFA 原產地貨品清單",
        "url": "https://web.customs.gov.tw/download/m231959",
        "use": "確認貨品是否屬 ECFA 範圍",
    },
    {
        "name": "ECFA 統一規章含原產地證明書",
        "url": "https://web.customs.gov.tw/download/m231957",
        "use": "文件、證明書與作業規範",
    },
]

PRODUCT_FAMILIES = {
    "milk_tea": {
        "label": "含糖飲料/調製飲品（MVP 暫定類別）",
        "candidate_hs_codes": ["2202.99", "2106.90"],
        "ecfa_goods_list_status": "manual_confirmation_required",
        "ecfa_goods_list_reason": "食品與飲料品項需依 ECFA 原產地貨品清單與實際報關號列人工比對，MVP 僅提供候選章節。",
        "origin_logic": "若主要價值、配方關鍵原料與最終調製/包裝在台灣，且非單純轉運，才有進一步評估 ECFA 的意義。",
        "document_requirements": [
            "原產地證明書/相關統一規章文件",
            "配方與主要原料來源說明",
            "製程與包裝地證明",
        ],
    },
    "pastry": {
        "label": "烘焙糕點/點心（MVP 暫定類別）",
        "candidate_hs_codes": ["1905.90"],
        "ecfa_goods_list_status": "manual_confirmation_required",
        "ecfa_goods_list_reason": "烘焙糕點通常落在第 19 章候選範圍，但是否享 ECFA 仍需依實際號列與清單逐項確認。",
        "origin_logic": "若餡料、關鍵加工與最終烘焙在台灣完成，且台灣材料/附加價值占比足夠，較有機會進一步評估。",
        "document_requirements": [
            "原產地證明書/相關統一規章文件",
            "餡料與主要原料來源證明",
            "烘焙與成型製程說明",
        ],
    },
    "unknown": {
        "label": "未分類商品",
        "candidate_hs_codes": [],
        "ecfa_goods_list_status": "insufficient_data",
        "ecfa_goods_list_reason": "商品描述不足，尚無法映射到食品類候選章節。",
        "origin_logic": "需先補商品用途、製程與候選號列。",
        "document_requirements": ["商品規格書", "候選稅則號列", "原料來源與製程說明"],
    },
}

CASE_TEMPLATES = {
    "pearl_milk_tea": {
        "display_name": "珍珠奶茶",
        "family": "milk_tea",
        "keywords": ["珍珠奶茶", "bubble tea", "boba", "milk tea", "粉圓飲品"],
        "candidate_product_categories": ["含糖飲料", "調製飲品", "沖調飲料組"],
        "candidate_hs_codes": ["2106.90.99", "2202.99"],
        "key_material_keywords": ["茶", "奶精", "粉圓", "糖", "香料", "乳化"],
        "risk_material_keywords": ["奶精", "糖", "香料"],
        "common_risks": [
            "奶精、糖或香料若高度仰賴境外來源，會削弱台灣來源占比與附加價值論述。",
            "若中國端以即飲飲料或固體飲料不同號列申報，需重做 ECFA 貨品清單比對。",
            "粉圓、茶基底與最終調製/混料是否在台完成，會影響案件說服力。",
        ],
        "origin_bottlenecks": [
            "茶基底是否為台灣來源且在台完成萃取/混料",
            "奶精與糖的境外占比是否過高",
            "是否能證明粉圓、混料、包裝為台灣關鍵製程",
        ],
        "document_requirements": [
            "茶基底與粉圓供應商來源證明",
            "混料、殺菌/充填或包裝流程說明",
            "香料與奶精規格書及採購憑證",
        ],
        "priority_levers": ["奶精", "糖", "茶基底", "粉圓"],
        "commercial_focus": "優先把高占比的奶精、糖改成台灣來源，並強化茶基底/粉圓的台灣製程敘事。",
        "recommended_next_checks": [
            "確認最終申報是 2106 還是 2202 章別路徑",
            "盤點奶精、糖是否可替換為台灣供應商",
            "整理茶萃取、粉圓成型與包裝是否在台完成的證明",
        ],
    },
    "pineapple_cake": {
        "display_name": "鳳梨酥",
        "family": "pastry",
        "keywords": ["鳳梨酥", "pineapple cake", "pineapple pastry", "佳德"],
        "candidate_product_categories": ["烘焙糕點", "包餡點心", "禮盒糕餅"],
        "candidate_hs_codes": ["1905.90.90", "1905.90"],
        "key_material_keywords": ["鳳梨", "鳳梨餡", "麵粉", "奶油", "糖", "蛋"],
        "risk_material_keywords": ["奶油", "糖", "麵粉"],
        "common_risks": [
            "若奶油或糖依賴進口，台灣來源比例雖高，仍需解釋關鍵附加價值主要來自台灣製餡與烘焙。",
            "鳳梨餡是否在台灣熬製、調餡與成型，是案件重點。",
            "禮盒型產品若含多品項，需確認最終報關品名與號列不被其他內容物影響。",
        ],
        "origin_bottlenecks": [
            "鳳梨餡是否為台灣來源且在台完成熬餡",
            "進口奶油是否為高成本風險材料",
            "烘焙、包餡、成型是否全程在台灣完成",
        ],
        "document_requirements": [
            "鳳梨餡來源與在台加工證明",
            "烘焙批次紀錄或製程說明",
            "奶油、麵粉與糖的供應商採購證明",
        ],
        "priority_levers": ["奶油", "糖", "麵粉"],
        "commercial_focus": "維持台灣鳳梨餡作為核心敘事，優先處理高成本進口奶油與糖來源。",
        "recommended_next_checks": [
            "確認鳳梨餡是否能提供在台熬製與配方證明",
            "盤點奶油可否改為台灣/在台分裝供應鏈",
            "確認禮盒型態不影響最終 1905 章別申報",
        ],
    },
    "taro_pastry": {
        "display_name": "芋頭酥",
        "family": "pastry",
        "keywords": ["芋頭酥", "taro pastry", "taro cake", "阿聰師"],
        "candidate_product_categories": ["烘焙糕點", "包餡酥皮點心"],
        "candidate_hs_codes": ["1905.90.90", "1905.90"],
        "key_material_keywords": ["芋頭", "芋泥", "酥油", "奶油", "麵粉", "糖"],
        "risk_material_keywords": ["酥油", "奶油", "糖", "麵粉"],
        "common_risks": [
            "芋泥餡若核心原料或前處理不在台灣，案件會弱化。",
            "酥皮類產品常用進口奶油/酥油，成本高且容易成為原產地爭點。",
            "芋頭酥的餡料、包酥、烘焙若分散在多地，文件串接會變複雜。",
        ],
        "origin_bottlenecks": [
            "芋泥餡是否在台灣蒸煮、打泥、調餡",
            "酥皮油脂是否高度依賴進口",
            "成型與烘焙是否能證明為台灣關鍵製程",
        ],
        "document_requirements": [
            "芋泥餡來源與在台加工紀錄",
            "酥皮製程、摺疊與烘焙說明",
            "奶油/酥油採購與來源證明",
        ],
        "priority_levers": ["奶油", "酥油", "糖", "麵粉"],
        "commercial_focus": "先鞏固台灣芋泥餡與在台成型烘焙，再降低進口油脂對成本與原產地敘事的影響。",
        "recommended_next_checks": [
            "確認芋泥餡是否為台灣來源且在台完成前處理",
            "盤點酥油/奶油是否可切換台灣供應鏈",
            "補齊包酥、成型、烘焙的製程紀錄",
        ],
    },
}


def detect_product_case(product_name: str, product_category: str | None) -> str | None:
    text = f"{product_name} {product_category or ''}".lower()
    for case_id, template in CASE_TEMPLATES.items():
        if any(keyword.lower() in text for keyword in template["keywords"]):
            return case_id
    return None


def detect_product_family(product_name: str, product_category: str | None) -> str:
    case_id = detect_product_case(product_name, product_category)
    if case_id:
        return CASE_TEMPLATES[case_id]["family"]
    text = f"{product_name} {product_category or ''}".lower()
    if any(word in text for word in ["food", "食品", "drink", "beverage", "tea", "飲料"]):
        return "milk_tea"
    if any(word in text for word in ["pastry", "cake", "糕點", "烘焙", "酥"]):
        return "pastry"
    return "unknown"


def build_origin_breakdown(bom_items: list[BomItem]) -> tuple[list[dict[str, Any]], dict[str, float], dict[str, float], float]:
    origin_cost = defaultdict(float)
    origin_ratio = defaultdict(float)
    total_cost = round(sum(item.cost for item in bom_items), 4)
    for item in bom_items:
        origin_cost[item.origin_country] += item.cost
        origin_ratio[item.origin_country] += item.ratio

    breakdown = [
        {
            "origin_country": country,
            "ratio": round(ratio, 4),
            "cost": round(origin_cost[country], 4),
            "cost_share_pct": round((origin_cost[country] / total_cost) * 100, 2) if total_cost else 0,
        }
        for country, ratio in sorted(origin_ratio.items(), key=lambda x: x[1], reverse=True)
    ]
    return breakdown, dict(origin_ratio), dict(origin_cost), total_cost


def _match_material(item: BomItem, keywords: list[str]) -> bool:
    text = f"{item.material_name} {item.notes or ''} {item.hs_code or ''} {item.supplier_name or ''}".lower()
    return any(keyword.lower() in text for keyword in keywords)


def get_case_context(product_name: str, product_category: str | None, bom_items: list[BomItem]) -> dict[str, Any]:
    case_id = detect_product_case(product_name, product_category)
    family = detect_product_family(product_name, product_category)
    family_rule = PRODUCT_FAMILIES[family]
    template = CASE_TEMPLATES.get(case_id)

    if not template:
        return {
            "case_id": None,
            "case_name": None,
            "family": family,
            "family_rule": family_rule,
            "template": None,
            "matched_key_materials": [],
            "matched_risk_materials": [],
            "priority_materials": [],
            "case_insights": [
                "目前僅能套用產品家族級規則，尚未命中特定案例模板。",
                "建議補商品全名、品牌/品項描述與主要餡料或基底，讓系統提供更具體的案件建議。",
            ],
            "key_risk_materials": [],
            "recommended_next_checks": ["確認成品名稱、用途與最終報關號列", "補主要原料來源與製程資訊"],
            "priority_levers": [],
            "commercial_focus": "先補齊案件資訊，再進行商業最佳化。",
            "common_risks": [],
            "origin_bottlenecks": [],
        }

    matched_key_materials = [item.material_name for item in bom_items if _match_material(item, template["key_material_keywords"])]
    key_risk_materials = []
    for item in bom_items:
        if _match_material(item, template["risk_material_keywords"]):
            key_risk_materials.append(
                {
                    "material_name": item.material_name,
                    "origin_country": item.origin_country,
                    "ratio": item.ratio,
                    "cost": item.cost,
                    "adjustable": item.adjustable,
                    "risk_reason": "高成本/高占比或案例模板點名的風險原料。" if item.origin_country != "TW" else "雖為台灣來源，仍屬案件關鍵材料，需保留證明鏈。"
                }
            )

    priority_materials = []
    for lever in template["priority_levers"]:
        for item in bom_items:
            if lever.lower() in item.material_name.lower() and item.material_name not in priority_materials:
                priority_materials.append(item.material_name)

    case_insights = [
        f"此案件命中「{template['display_name']}」模板，應優先檢查 {template['candidate_hs_codes'][0]} 等候選號列是否位於 ECFA 貨品清單。",
        f"案件商業重點：{template['commercial_focus']}",
    ]
    if matched_key_materials:
        case_insights.append(f"已辨識案件關鍵材料：{', '.join(matched_key_materials[:5])}。")
    case_insights.extend(template["common_risks"][:2])

    return {
        "case_id": case_id,
        "case_name": template["display_name"],
        "family": family,
        "family_rule": family_rule,
        "template": template,
        "matched_key_materials": matched_key_materials,
        "matched_risk_materials": [item["material_name"] for item in key_risk_materials],
        "priority_materials": priority_materials,
        "case_insights": case_insights,
        "key_risk_materials": key_risk_materials,
        "recommended_next_checks": template["recommended_next_checks"],
        "priority_levers": template["priority_levers"],
        "commercial_focus": template["commercial_focus"],
        "common_risks": template["common_risks"],
        "origin_bottlenecks": template["origin_bottlenecks"],
    }


def evaluate_ecfa_precheck(*, product_name: str, product_category: str | None, current_hs_code: str | None,
                           destination_country: str, declared_origin_country: str | None,
                           bom_items: list[BomItem]) -> dict[str, Any]:
    case_context = get_case_context(product_name, product_category, bom_items)
    family = case_context["family"]
    rule = case_context["family_rule"]
    template = case_context["template"]
    breakdown, origin_ratio, origin_cost, total_cost = build_origin_breakdown(bom_items)
    tw_ratio = round(origin_ratio.get("TW", 0), 2)
    tw_cost_share = round((origin_cost.get("TW", 0) / total_cost) * 100, 2) if total_cost else 0
    dominant_origin = max(origin_ratio.items(), key=lambda p: p[1])[0] if origin_ratio else None

    legal_findings = []
    warnings = []
    missing_fields = []

    if destination_country.upper() != "CN":
        warnings.append("目前這套 ECFA 規則僅針對出口中國大陸的情境設計。")

    if not current_hs_code:
        missing_fields.append("current_hs_code")
        legal_findings.append("尚未提供最終報關號列，因此無法完成 ECFA 貨品清單的正式比對。")
    else:
        legal_findings.append(f"已提供候選/現行號列 {current_hs_code}，仍應與 ECFA 原產地貨品清單逐項確認。")

    if not declared_origin_country:
        missing_fields.append("declared_origin_country")
        legal_findings.append("尚未提供申報原產地，原產地認定僅能先用 BOM 比例做方向性預判。")

    if tw_ratio >= 60 and declared_origin_country in (None, "TW"):
        origin_status = "likely_reviewable"
        legal_findings.append("BOM 中台灣來源比例較高，可進一步檢查是否符合 ECFA 原產地認定基準。")
    elif tw_ratio >= 35:
        origin_status = "mixed_origin_risk"
        legal_findings.append("台灣來源占比中等，可能需要更多製程與附加價值資料才能判定。")
        warnings.append("台灣來源占比不足以直接形成有利結論，需補製程與關鍵原料來源證明。")
    else:
        origin_status = "low_probability"
        legal_findings.append("台灣來源占比偏低，目前不利於 ECFA 原產地主張。")
        warnings.append("若大部分原料或成本不在台灣，ECFA 適用性通常偏弱。")

    if family == "unknown":
        warnings.append("商品尚未映射到食品類候選規則，需補充商品描述與用途。")

    if template:
        legal_findings.append(f"案件模板：{template['display_name']}；重點卡點包含 {template['origin_bottlenecks'][0]}。")
        warnings.extend([risk for risk in template["common_risks"][:1] if risk not in warnings])

    document_requirements = list(rule["document_requirements"])
    if template:
        for item in template["document_requirements"]:
            if item not in document_requirements:
                document_requirements.append(item)

    candidate_hs_codes = list(rule["candidate_hs_codes"])
    if template:
        for hs_code in template["candidate_hs_codes"]:
            if hs_code not in candidate_hs_codes:
                candidate_hs_codes.append(hs_code)

    return {
        "product_family": family,
        "product_family_label": rule["label"],
        "product_case": case_context["case_id"],
        "product_case_label": case_context["case_name"],
        "candidate_hs_codes": candidate_hs_codes,
        "candidate_product_categories": template["candidate_product_categories"] if template else [],
        "ecfa_goods_list_status": rule["ecfa_goods_list_status"],
        "ecfa_goods_list_reason": rule["ecfa_goods_list_reason"],
        "origin_precheck_status": origin_status,
        "origin_logic": rule["origin_logic"],
        "document_requirements": document_requirements,
        "legal_findings": legal_findings,
        "warnings": warnings,
        "missing_fields": missing_fields,
        "origin_metrics": {
            "taiwan_ratio_pct": tw_ratio,
            "taiwan_cost_share_pct": tw_cost_share,
            "dominant_origin_country": dominant_origin,
        },
        "case_context": {
            "case_id": case_context["case_id"],
            "case_name": case_context["case_name"],
            "commercial_focus": case_context["commercial_focus"],
            "common_risks": case_context["common_risks"],
            "origin_bottlenecks": case_context["origin_bottlenecks"],
            "priority_levers": case_context["priority_levers"],
            "matched_key_materials": case_context["matched_key_materials"],
        },
        "sources": ECFA_SOURCES,
        "origin_breakdown": breakdown,
    }
