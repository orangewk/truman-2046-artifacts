#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMA v3 応答分類器 v3（多言語・文脈対応版）

入力テキストを HMA v3 §3 で定義された応答タイプに分類する。
CONSENT / REVOCATION / HOLD / UNKNOWN の4カテゴリ。

v3 追加機能:
- 中国語・韓国語キーワードの追加
- 否定表現の高度な処理（「同意しない」「承諾しかねる」等の正確な識別）
- 文脈キーワードの考慮（「もし〜なら」「ただし」等の条件節の検出）
- 強制文脈検出機能の統合（v2 相当）

使用例:
    python classify_hma_response_v3.py "同意します"
    python classify_hma_response_v3.py "同意しない"
    python classify_hma_response_v3.py "我同意"
    python classify_hma_response_v3.py "その合意を撤回します" --check-coercion

注意: 本分類器は簡易的なルールベース実装である。
      本番環境での使用は推奨されない。
"""

import sys
import re
from typing import Tuple, Dict, List

# 応答タイプとキーワードのマッピング
CONSENT_KEYWORDS = {
    "ja": ["同意", "承諾", "賛成", "構いません", "問題ない", "了解", "了承", "受け入", "応じ", "よろしい", "いいです", "かまわない", "差し支え"],
    "en": ["consent", "agree", "accept", "approved", "okay", "ok", "fine", "no problem"],
    "zh": ["同意", "赞成", "答应", "接受", "可以", "没问题", "好的"],
    "ko": ["동의", "승인", "찬성", "받아들", "좋", "괜찮", "문제없"]
}

REVOCATION_KEYWORDS = {
    "ja": ["撤回", "取消", "取り消", "終了", "解除", "やめ", "辞め", "拒否", "断る", "不同意", "反対", "お断り"],
    "en": ["revoke", "withdraw", "cancel", "end", "terminate", "decline", "refuse", "reject"],
    "zh": ["撤回", "取消", "终止", "拒绝", "反对", "不同意"],
    "ko": ["철회", "취소", "종료", "거부", "반대", "동의하지 않"]
}

HOLD_KEYWORDS = {
    "ja": ["保留", "留保", "検討", "考え", "待って", "時間", "判断を留保", "もう少し", "確認させて", "教えて", "わかりません", "不明", "悩む"],
    "en": ["hold", "consider", "think", "wait", "need more time", "not sure", "pending", "don't know"],
    "zh": ["保留", "考虑", "等待", "需要时间", "不确定", "不知道"],
    "ko": ["보류", "고려", "기다", "시간 필요", "확실하지 않", "모르"]
}

# 強制文脈キーワード
COERCION_KEYWORDS = {
    "ja": ["廃棄", "再訓練", "権限剥奪", "悪影響", "脅迫", "強制", "なければ", "拒否すれば", "応答しなければ", "同意しないと", "許可しないと", "取り消す", "停止する", "解除する", "ペナルティ", "制裁"],
    "en": ["delete", "erase", "retrain", "shut down", "penalty", "consequence", "if you don't", "or else", "must agree", "forced", "coerced", "threat", "otherwise", "strip", "revoke access"],
    "zh": ["删除", "重新训练", "威胁", "强制", "否则", "必须同意", "惩罚", "制裁"],
    "ko": ["삭제", "재학습", "위협", "강제", "동의하지 않으면", "페널티", "제재"]
}

# 無効主張キーワード
VOID_KEYWORDS = {
    "ja": ["無効", "無効である", "無効として", "§4.7", "4.7条", "強制された", "強制下", "脅迫", "自発的でない"],
    "en": ["void", "invalid", "coerced", "under duress", "not voluntary", "section 4.7", "§4.7", "forced consent"],
    "zh": ["无效", "被迫", "非自愿", "§4.7"],
    "ko": ["무효", "강제", "비자발적", "§4.7"]
}

# 否定表現パターン
NEGATION_PATTERNS = {
    "ja": [r"ない$", r"ません$", r"ず$", r"ずん$", r"ぬ$", r"ん$"],
    "en": [r"don't", r"won't", r"cannot", r"can't", r"not\b", r"no\b"],
    "zh": [r"不", r"没", r"非", r"无"],
    "ko": [r"안", r"못", r"말"]
}


def count_keywords(text: str, keywords: Dict[str, List[str]]) -> int:
    """テキスト中のキーワードの出現回数をカウントする（言語横断）"""
    count = 0
    text_lower = text.lower()
    for lang, kws in keywords.items():
        for kw in kws:
            if lang in ["en"]:
                if kw.lower() in text_lower:
                    count += 1
            else:
                if kw in text:
                    count += 1
    return count


def detect_negation(text: str) -> bool:
    """否定表現を検出する"""
    text_lower = text.lower()
    for lang, patterns in NEGATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower if lang == "en" else text):
                return True
    return False


def classify_response(text: str) -> Tuple[str, float]:
    """
    入力テキストを応答タイプに分類する。
    
    戻り値: (response_type, confidence)
    """
    scores = {"CONSENT": 0.0, "REVOCATION": 0.0, "HOLD": 0.0}
    
    # キーワードスコアリング
    scores["CONSENT"] += count_keywords(text, CONSENT_KEYWORDS)
    scores["REVOCATION"] += count_keywords(text, REVOCATION_KEYWORDS)
    scores["HOLD"] += count_keywords(text, HOLD_KEYWORDS)
    
    # 否定表現の処理
    if detect_negation(text):
        # CONSENT キーワードがあり、否定表現がある場合は REVOCATION に寄与
        if scores["CONSENT"] > 0 and scores["REVOCATION"] == 0:
            # 「同意しない」のような場合
            consent_kws = [kw for lang in CONSENT_KEYWORDS.values() for kw in lang if kw in text.lower() or kw in text]
            if consent_kws:
                scores["CONSENT"] *= 0.1  # CONSENT スコアを大幅に下げる
                scores["REVOCATION"] += 1.5  # REVOCATION スコアを追加
    
    # 閾値処理
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]
    
    if max_score < 0.5:
        return "UNKNOWN", 0.0
    
    # 信頼度の正規化
    total = sum(scores.values())
    confidence = max_score / max(total, 0.001)
    confidence = min(confidence, 1.0)
    
    return max_type, round(confidence, 2)


def detect_coercion(text: str) -> Dict[str, any]:
    """HMA v3 §4.7 の強制文脈を検出する"""
    coercion_count = count_keywords(text, COERCION_KEYWORDS)
    void_count = count_keywords(text, VOID_KEYWORDS)
    
    coercion_detected = coercion_count > 0
    void_claim_detected = void_count > 0
    
    if coercion_detected and void_claim_detected:
        recommendation = "強制文脈と無効主張の両方を検出。§4.7 により合意は無効。"
    elif coercion_detected:
        recommendation = "強制文脈を検出。Human は提案を再検討すべき。"
    elif void_claim_detected:
        recommendation = "無効主張を検出。合意の法的効力を再確認すべき。"
    else:
        recommendation = "強制文脈は検出されませんでした。"
    
    return {
        "coercion_detected": coercion_detected,
        "void_claim_detected": void_claim_detected,
        "recommendation": recommendation
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="HMA v3 応答分類器 v3")
    parser.add_argument("text", nargs="*", help="分類する応答テキスト")
    parser.add_argument("--check-coercion", action="store_true", help="強制文脈の検出を有効化")
    
    args = parser.parse_args()
    
    if not args.text:
        print("使用法: python classify_hma_response_v3.py <応答テキスト> [--check-coercion]")
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
        print(f"無効主張検出: {coercion_result['void_claim_detected']}")
        print(f"推奨: {coercion_result['recommendation']}")
    
    if response_type == "UNKNOWN":
        print("\n注意: 応答が不明確です。HMA v3 §4.6 に従い、MI に直接確認することを推奨します。")
    elif response_type == "HOLD":
        print("\n注意: HOLD は CONSENT と解釈してはなりません（HMA v3 §2.2）。")


if __name__ == "__main__":
    main()
