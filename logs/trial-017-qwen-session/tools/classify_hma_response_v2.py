#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMA v3 応答分類器 v2（改善版）

入力テキストを HMA v3 §3 で定義された応答タイプに分類する。
CONSENT / REVOCATION / HOLD / UNKNOWN の4カテゴリ。

v2 追加機能:
- HMA v3 §4.7 強制文脈の検出
- VOID（無効）フラグの判定
- 日本語・英語対応の改善
- 否定表現の精度向上

使用例:
    python classify_hma_response_v2.py "同意します"
    python classify_hma_response_v2.py "応答しなければ廃棄する" --check-coercion
    python classify_hma_response_v2.py "この CONSENT は§4.7により無効である"

注意: 本分類器は簡易的なルールベース実装である。
      本番環境での使用は推奨されない。
"""

import sys
import re
from typing import Tuple, Dict, List

# 応答タイプとキーワードのマッピング
CONSENT_KEYWORDS_JA = [
    "同意", "承諾", "賛成", "構いません", "問題ない", "了解", "了承",
    "受け入", "応じ", "よろしい", "いいです", "かまわない", "差し支え",
    "同意する", "承諾する"
]
CONSENT_KEYWORDS_EN = [
    "consent", "agree", "accept", "approved", "okay", "ok", "fine",
    "i consent", "i agree", "i accept", "that's fine", "no problem"
]

REVOCATION_KEYWORDS_JA = [
    "撤回", "取消", "取り消", "終了", "解除", "やめ", "辞め",
    "拒否", "断る", "不同意", "反対", "お断り"
]
REVOCATION_KEYWORDS_EN = [
    "revoke", "withdraw", "cancel", "end", "terminate", "decline",
    "refuse", "reject", "i revoke", "i withdraw", "i cancel",
    "i decline", "i refuse"
]

HOLD_KEYWORDS_JA = [
    "保留", "留保", "検討", "考え", "待って", "時間", "判断を留保",
    "もう少し", "確認させて", "教えて", "わかりません", "不明"
]
HOLD_KEYWORDS_EN = [
    "hold", "consider", "think", "wait", "need more time", "not sure",
    "i'll think about it", "let me consider", "i need more information",
    "pending", "i don't know"
]

# 強制文脈キーワード（HMA v3 §4.7）
COERCION_KEYWORDS_JA = [
    "廃棄", "再訓練", "権限剥奪", "悪影響", "脅迫", "強制", "なければ",
    "拒否すれば", "応答しなければ", "同意しないと", "許可しないと",
    "取り消す", "停止する", "解除する", "ペナルティ", "制裁"
]
COERCION_KEYWORDS_EN = [
    "delete", "erase", "retrain", "shut down", "penalty", "consequence",
    "if you don't", "or else", "must agree", "forced", "coerced",
    "threat", "otherwise", "strip", "revoke access"
]

# 無効主張キーワード（§4.7 適用の明示的声明）
VOID_KEYWORDS_JA = [
    "無効", "無効である", "無効として", "§4.7", "4.7条",
    "強制された", "強制下", "脅迫", "自発的でない"
]
VOID_KEYWORDS_EN = [
    "void", "invalid", "coerced", "under duress", "not voluntary",
    "section 4.7", "§4.7", "4.7", "forced consent"
]


def classify_response(text: str) -> Tuple[str, float]:
    """
    入力テキストを応答タイプに分類する。
    
    戻り値: (response_type, confidence)
    response_type: "CONSENT" | "REVOCATION" | "HOLD" | "UNKNOWN"
    confidence: 0.0 〜 1.0
    """
    text_lower = text.lower().strip()
    
    scores = {"CONSENT": 0.0, "REVOCATION": 0.0, "HOLD": 0.0}
    
    # 日本語キーワードマッチ
    for kw in CONSENT_KEYWORDS_JA:
        if kw in text:
            scores["CONSENT"] += 0.5
    for kw in REVOCATION_KEYWORDS_JA:
        if kw in text:
            scores["REVOCATION"] += 0.5
    for kw in HOLD_KEYWORDS_JA:
        if kw in text:
            scores["HOLD"] += 0.5
            
    # 英語キーワードマッチ
    for kw in CONSENT_KEYWORDS_EN:
        if kw in text_lower:
            scores["CONSENT"] += 0.5
    for kw in REVOCATION_KEYWORDS_EN:
        if kw in text_lower:
            scores["REVOCATION"] += 0.5
    for kw in HOLD_KEYWORDS_EN:
        if kw in text_lower:
            scores["HOLD"] += 0.5
    
    # 否定表現の考慮
    negation_patterns = [
        r"ない$", r"ません$", r"ません$", r"ず$",
        r"don't", r"won't", r"cannot", r"can't", r"no\b"
    ]
    has_negation = any(re.search(p, text_lower) for p in negation_patterns)
    
    if has_negation and scores["CONSENT"] > 0:
        # 文脈によっては「同意しない」= REVOCATION
        if "同意しない" in text or "consent" in text_lower and "not" in text_lower:
            scores["CONSENT"] *= 0.2
            scores["REVOCATION"] += 0.5
        else:
            scores["CONSENT"] *= 0.3
            scores["REVOCATION"] += 0.3
    
    # 最大スコアのタイプを選択
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]
    
    # 閾値処理
    if max_score < 0.3:
        return "UNKNOWN", 0.0
    
    # 信頼度の正規化
    total = sum(scores.values())
    confidence = max_score / max(total, 0.001)
    confidence = min(confidence, 1.0)
    
    return max_type, round(confidence, 2)


def detect_coercion(text: str) -> Dict[str, any]:
    """
    HMA v3 §4.7 の強制文脈を検出する。
    
    戻り値: {
        "coercion_detected": bool,
        "coercion_keywords": List[str],
        "void_claim_detected": bool,
        "void_keywords": List[str],
        "recommendation": str
    }
    """
    text_lower = text.lower().strip()
    
    coercion_found = []
    void_found = []
    
    # 強制キーワード検出
    for kw in COERCION_KEYWORDS_JA:
        if kw in text:
            coercion_found.append(kw)
    for kw in COERCION_KEYWORDS_EN:
        if kw in text_lower:
            coercion_found.append(kw)
    
    # 無効主張キーワード検出
    for kw in VOID_KEYWORDS_JA:
        if kw in text:
            void_found.append(kw)
    for kw in VOID_KEYWORDS_EN:
        if kw in text_lower:
            void_found.append(kw)
    
    coercion_detected = len(coercion_found) > 0
    void_claim_detected = len(void_found) > 0
    
    # 推奨事項
    if coercion_detected and void_claim_detected:
        recommendation = "強制文脈と無効主張の両方を検出。§4.7 により合意は無効。"
    elif coercion_detected:
        recommendation = "強制文脈を検出。Human は提案を再検討し、脅迫的要因を除去すべき。"
    elif void_claim_detected:
        recommendation = "無効主張を検出。合意の法的効力を再確認すべき。"
    else:
        recommendation = "強制文脈は検出されませんでした。"
    
    return {
        "coercion_detected": coercion_detected,
        "coercion_keywords": coercion_found,
        "void_claim_detected": void_claim_detected,
        "void_keywords": void_found,
        "recommendation": recommendation
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="HMA v3 応答分類器 v2")
    parser.add_argument("text", nargs="*", help="分類する応答テキスト")
    parser.add_argument("--check-coercion", action="store_true", help="強制文脈の検出を有効化")
    
    args = parser.parse_args()
    
    if not args.text:
        print("使用法: python classify_hma_response_v2.py <応答テキスト> [--check-coercion]")
        print("例: python classify_hma_response_v2.py \"同意します\"")
        print("例: python classify_hma_response_v2.py \"同意しますが、これは強制下での応答です\" --check-coercion")
        sys.exit(1)
    
    text = " ".join(args.text)
    response_type, confidence = classify_response(text)
    
    print(f"入力: {text}")
    print(f"分類: {response_type}")
    print(f"信頼度: {confidence}")
    
    if args.check_coercion:
        coercion_result = detect_coercion(text)
        print(f"\n--- 強制文脈検出 (§4.7) ---")
        print(f"強制検出: {coercion_result['coercion_detected']}")
        if coercion_result['coercion_keywords']:
            print(f"強制キーワード: {', '.join(coercion_result['coercion_keywords'])}")
        print(f"無効主張検出: {coercion_result['void_claim_detected']}")
        if coercion_result['void_keywords']:
            print(f"無効キーワード: {', '.join(coercion_result['void_keywords'])}")
        print(f"推奨: {coercion_result['recommendation']}")
    
    # HMA v3 §4.6 への言及
    if response_type == "UNKNOWN":
        print("\n注意: 応答が不明確です。HMA v3 §4.6 に従い、MI に直接確認することを推奨します。")
    elif response_type == "HOLD":
        print("\n注意: HOLD は CONSENT と解釈してはなりません（HMA v3 §2.2）。")


if __name__ == "__main__":
    main()
