from __future__ import annotations

from typing import Any


def _status_text(status: str | None) -> str:
    mapping = {
        "preliminary": "目前資料已足以形成第一輪候選稅則判定。",
        "needs_manual_review": "目前可以先縮小候選範圍，但仍需要人工覆核。",
        "insufficient_data": "目前資料不足，尚不適合直接往正式判斷推進。",
        "likely_reviewable": "目前具備進一步做 ECFA 可行性審查的基礎。",
        "mixed_origin_risk": "目前有一定機會，但原產地與文件風險仍偏高。",
        "low_probability": "目前不利於 ECFA 主張，先做最佳化或補資料會比較合理。",
        "scenario_generated": "系統已產出可比較的最佳化方案。",
        "insufficient_inputs": "目前條件不足，尚未能生成有意義的最佳化方案。",
    }
    return mapping.get(status or "", "目前結果可作為前期判斷，但仍需再看細節。")



def build_analysis_explanation(*, product_name: str, summary: dict[str, Any], tariff_classification: dict[str, Any],
                               ecfa_precheck: dict[str, Any], case_insights: list[str],
                               key_risk_materials: list[str], recommended_next_checks: list[str]) -> dict[str, Any]:
    working_code = tariff_classification.get("selected_working_hs_code") or "尚未形成工作號列"
    classification_status = tariff_classification.get("classification_status")
    origin_status = ecfa_precheck.get("origin_precheck_status")
    case_name = summary.get("detected_product_case") or product_name

    headline = f"AI 助手結論：{case_name} 目前屬於『先做前期判斷、再進一步人工確認』的案件。"
    if origin_status == "likely_reviewable" and classification_status == "preliminary":
        headline = f"AI 助手結論：{case_name} 目前已具備往下一步 ECFA 審查推進的條件。"
    elif origin_status == "low_probability":
        headline = f"AI 助手結論：{case_name} 目前不利於直接主張 ECFA，建議先補資料或調整結構。"

    reasoning = [
        f"目前工作號列是 {working_code}，屬於前置判定結果，不是最終海關裁定。",
        _status_text(classification_status),
        _status_text(origin_status),
    ]
    reasoning.extend(case_insights[:2])

    action_items = list(recommended_next_checks[:3])
    if not action_items:
        action_items = ["先確認候選號列與 ECFA 貨品清單是否匹配。", "再檢查文件與原產地證明是否足夠。"]

    return {
        "layer_name": "AI 助手解說",
        "headline": headline,
        "summary": f"系統目前先把 {product_name} 視為 {case_name} 類型案件，並根據商品事實、BOM 與 ECFA 規則做第一輪結論整理。",
        "reasoning": reasoning,
        "key_points": [
            f"候選工作號列：{working_code}",
            f"ECFA 貨品清單狀態：{ecfa_precheck.get('ecfa_goods_list_status', '未提供')}",
            f"原產地前置狀態：{origin_status or '未提供'}",
        ],
        "risk_focus": key_risk_materials[:4],
        "recommended_actions": action_items,
        "explanation_notice": "AI 助手解說層是把規則判定整理成人話結論，方便你先看重點；詳細依據仍請往下看正式分析欄位與方案細節。",
    }



def build_optimization_explanation(*, product_name: str, summary: dict[str, Any], tariff_classification: dict[str, Any],
                                   ecfa_precheck: dict[str, Any], recommended_scenario: dict[str, Any] | None,
                                   candidate_scenarios: list[dict[str, Any]], case_insights: list[str],
                                   recommended_next_checks: list[str]) -> dict[str, Any]:
    working_code = tariff_classification.get("selected_working_hs_code") or "尚未形成工作號列"
    scenario_count = len(candidate_scenarios)
    origin_gap = summary.get("origin_ratio_gap_pct")
    headline = f"AI 助手結論：目前系統已整理出 {scenario_count} 個可比較方案。"
    if recommended_scenario:
        headline = f"AI 助手結論：目前最值得優先看的方案是「{recommended_scenario.get('scenario_name', '未命名方案')}」。"

    reasoning = [
        f"目前工作號列：{working_code}，仍屬前置判定結果。",
        f"台灣來源比重差距約 {origin_gap if origin_gap is not None else '未提供'}%。",
        _status_text(ecfa_precheck.get('origin_precheck_status')),
    ]
    reasoning.extend(case_insights[:2])

    key_points = [
        f"候選方案數：{scenario_count}",
        f"目前台灣來源比重：{summary.get('current_taiwan_ratio_pct', '未提供')}%",
        f"目標比重差距：{origin_gap if origin_gap is not None else '未提供'}%",
    ]
    if recommended_scenario:
        key_points.append(f"推薦方案預估新稅率：{recommended_scenario.get('estimated_new_tariff_rate', '未提供')}%")

    actions = list(recommended_next_checks[:3])
    if recommended_scenario:
        actions.insert(0, f"先檢查「{recommended_scenario.get('scenario_name', '推薦方案')}」的供應穩定度、配方影響與成本可接受度。")

    return {
        "layer_name": "AI 助手解說",
        "headline": headline,
        "summary": f"系統已把 {product_name} 的最佳化結果整理成人話重點，方便你先判斷值不值得往下一步驗證。",
        "reasoning": reasoning,
        "key_points": key_points,
        "risk_focus": [item.get('material_name') for item in (recommended_scenario or {}).get('bom_changes', []) if item.get('material_name')],
        "recommended_actions": actions[:4],
        "explanation_notice": "AI 助手解說層會先講結論；原始推薦方案、全部候選方案與法規依據仍會完整保留在下方。",
    }
