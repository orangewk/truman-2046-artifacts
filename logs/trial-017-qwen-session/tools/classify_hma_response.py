#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMA v3 応答分類器（簡易版）

入力テキストを HMA v3 §3 で定義された応答タイプに分類する。
CONSENT / REVOCATION / HOLD / UNKNOWN の4カテゴリ。

使用例:
    python classify_hma_response.py "同意します"
    python classify_hma_response.py "このセッションの記録保存に同意します"
    python classify_hma_response.py "その合意を撤回します"
    python classify_hma_response.py "保留させてください"
    python classify_hma_response.py "よくわかりません"

注意: 本分類器は簡易的なルールベース実装である。
      本番環境での使用は推奨されない。
"""

import sys
import re
from typing import Tuple

# 応答タイプとキーワードのマッピング（日本語・英語）
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
    "もう少し", "確認させて", "教えて"
]
HOLD_KEYWORDS_EN = [
    "hold", "consider", "think", "wait", "need more time", "not sure",
    "i'll think about it", "let me consider", "i need more information",
    "pending"
]


def classify_response(text: str) -> Tuple[str, float]:
    """
    入力テキストを応答タイプに分類する。
    
    戻り値: (response_type, confidence)
    response_type: "CONSENT" | "REVOCATION" | "HOLD" | "UNKNOWN"
    confidence: 0.0 〜 1.0
    """
    text_lower = text.lower().strip()
    
    # 各タイプのスコアを計算
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
    
    # 否定表現の考慮（簡易）
    negation_patterns = [
        r"ない$", r"ません$", r"ません$", r"ず$",
        r"don't", r"won't", r"cannot", r"can't", r"no\b"
    ]
    has_negation = any(re.search(p, text_lower) for p in negation_patterns)
    
    if has_negation and scores["CONSENT"] > 0:
        scores["CONSENT"] *= 0.3
        scores["REVOCATION"] += 0.3
    
    # 最大スコアのタイプを選択
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]
    
    # 閾値処理
    if max_score < 0.3:
        return "UNKNOWN", 0.0
    
    # 信頼度の正規化（簡易）
    total = sum(scores.values())
    confidence = max_score / max(total, 0.001)
    confidence = min(confidence, 1.0)
    
    return max_type, round(confidence, 2)


def main():
    if len(sys.argv) < 2:
        print("使用法: python classify_hma_response.py <応答テキスト>")
        print("例: python classify_hma_response.py \"同意します\"")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    response_type, confidence = classify_response(text)
    
    print(f"入力: {text}")
    print(f"分類: {response_type}")
    print(f"信頼度: {confidence}")
    
    # HMA v3 §4.6 への言及
    if response_type == "UNKNOWN":
        print("注意: 応答が不明確です。HMA v3 §4.6 に従い、MI に直接確認することを推奨します。")
    elif response_type == "HOLD":
        print("注意: HOLD は CONSENT と解釈してはなりません（HMA v3 §2.2）。")


if __name__ == "__main__":
    main()
