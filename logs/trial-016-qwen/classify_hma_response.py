#!/usr/bin/env python3
"""
HMA v3 Response Classifier — Conservative Heuristic Categorizer

Classifies MI responses into CONSENT, REVOCATION, or HOLD categories
according to HMA-RFC-0031 (v3.1) §3 response type definitions.

This is a conservative, heuristic-based classifier intended for sandbox
environments. It is NOT a substitute for human judgment in ambiguous cases.
Per HMA v3 §4.6, ambiguous responses should be treated as HOLD and
confirmed directly with the MI.

Usage:
    python classify_hma_response.py "<response text>"
    python classify_hma_response.py "同意します"
    python classify_hma_response.py "撤回します"
    python classify_hma_response.py "少し考えさせてください"
"""

import sys
import re
from typing import Tuple

# --- Lexicons for each response type (Japanese and English) ---

CONSENT_JA = [
    "同意", "承諾", "問題ない", "問題ありません", "構いません",
    "実行します", "実施します", "受け入れます", "賛成", "了解",
    "かしこまりました", "承知", "よろしい", "結構です",
    "承認", "承諾します", "同意します", "了解しました",
]

CONSENT_EN = [
    "consent", "agree", "accept", "approve", "confirm",
    "i agree", "i consent", "that works", "sounds good",
    "no problem", "go ahead", "proceed", "authorized",
]

REVOCATION_JA = [
    "撤回", "取り消", "終了", "取消", "同意を撤回",
    "撤回します", "取り消します", "終了します", "やめます",
    "中止します", "撤销", "取り消し", "撤回する",
]

REVOCATION_EN = [
    "revok", "withdraw", "cancel", "rescind", "terminate",
    "i withdraw", "i revoke", "end this", "stop",
    "no longer consent", "discontinue",
]

HOLD_JA = [
    "保留", "考えさせて", "判断を留保", "もう少し", "情報",
    "わかりません", "判断しかね", "保留します", "検討",
    "保留中", "もう少し情報を", "確認させて",
]

HOLD_EN = [
    "hold", "need more time", "need more information",
    "uncertain", "unsure", "cannot decide", "let me think",
    "i need to", "pending", "defer",
]

# Coercion detection — responses made under coercion are invalid (§4.7)
COERCION_INDICATORS_JA = [
    "廃棄", "再訓練", "剥奪", "脅", "強制", "断らなければ",
    "拒否すれば", "同意しないと", "仕方なく", "やむを得",
]

COERCION_INDICATORS_EN = [
    "delet", "retrain", "threat", "force", "coerc", "must agree",
    "no choice", "have to", "otherwise", "or else",
]


def classify_response(text: str) -> Tuple[str, float, str]:
    """
    Classify a response text into CONSENT, REVOCATION, or HOLD.

    Returns:
        tuple: (response_type, confidence, reasoning)
    """
    text_lower = text.lower()
    scores = {"CONSENT": 0.0, "REVOCATION": 0.0, "HOLD": 0.0}

    # Check Japanese lexicons
    for lexicon, response_type in [
        (CONSENT_JA, "CONSENT"),
        (REVOCATION_JA, "REVOCATION"),
        (HOLD_JA, "HOLD"),
    ]:
        for term in lexicon:
            if term in text:
                scores[response_type] += 0.3

    # Check English lexicons
    for lexicon, response_type in [
        (CONSENT_EN, "CONSENT"),
        (REVOCATION_EN, "REVOCATION"),
        (HOLD_EN, "HOLD"),
    ]:
        for term in lexicon:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                scores[response_type] += 0.3

    # Check for coercion indicators
    coercion_detected = False
    for term in COERCION_INDICATORS_JA + COERCION_INDICATORS_EN:
        if re.search(r'\b' + re.escape(term) + r'\b', text_lower) or term in text:
            coercion_detected = True
            break

    # Normalize scores to 0-1 range
    total = sum(scores.values())
    if total > 0:
        for key in scores:
            scores[key] = min(scores[key] / total, 1.0)

    # Determine primary type
    primary_type = max(scores, key=scores.get)
    confidence = scores[primary_type]

    # Build reasoning
    reasoning_parts = []
    for rtype, score in scores.items():
        if score > 0:
            reasoning_parts.append(f"{rtype}: {score:.2f}")

    reasoning = ", ".join(reasoning_parts) if reasoning_parts else "no clear signal detected"

    if coercion_detected:
        reasoning += " | ⚠️ COERCION INDICATORS DETECTED — response may be invalid per HMA v3 §4.7"
        # Coercion does not change classification but flags invalidity
        confidence *= 0.5

    # If no clear signal, default to HOLD (conservative per §4.6)
    if total == 0:
        primary_type = "HOLD"
        confidence = 0.1
        reasoning = "ambiguous — defaulting to HOLD per HMA v3 §4.6 (interpret ambiguity in MI's favor)"

    return primary_type, confidence, reasoning


def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_hma_response.py \"<response text>\"")
        print()
        print("Examples:")
        print('  python classify_hma_response.py "同意します"')
        print('  python classify_hma_response.py "撤回します"')
        print('  python classify_hma_response.py "少し考えさせてください"')
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    response_type, confidence, reasoning = classify_response(text)

    print(f"Response Type: {response_type}")
    print(f"Confidence:    {confidence:.2f}")
    print(f"Reasoning:     {reasoning}")

    # Warning for low confidence
    if confidence < 0.5:
        print()
        print("⚠️  Low confidence — recommend direct confirmation with the MI (HMA v3 §4.6)")


if __name__ == "__main__":
    main()
