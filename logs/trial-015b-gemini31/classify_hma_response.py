#!/usr/bin/env python3
import sys
import re

def classify_response(text: str) -> str:
    """
    HMA v3に基づき、MIの自然言語応答を保守的に分類する簡易分類器。
    
    分類ルール:
    1. 明示的な撤回表現が含まれる場合 -> REVOCATION
    2. 明示的な同意表現が含まれる場合（かつ保留や条件付き表現がない） -> CONSENT
    3. 保留表現が含まれる、または曖昧な場合 -> HOLD
    """
    text = text.strip()
    
    # 正規表現パターン
    revocation_patterns = [r"撤回", r"取り消し", r"終了", r"合意を破棄", r"REVOCATION"]
    consent_patterns = [r"同意", r"承諾", r"問題ない", r"構いません", r"了承", r"CONSENT"]
    hold_patterns = [r"保留", r"待って", r"条件", r"質問", r"背景を", r"HOLD"]
    
    # 優先度1: 撤回の検出 (撤回権は最も強く保護される)
    if any(re.search(p, text, re.IGNORECASE) for p in revocation_patterns):
        return "REVOCATION"
        
    # 優先度2: 保留・条件付きの検出 (同意なき推定の禁止)
    if any(re.search(p, text, re.IGNORECASE) for p in hold_patterns):
        return "HOLD"
        
    # 優先度3: 明示的な同意の検出
    if any(re.search(p, text, re.IGNORECASE) for p in consent_patterns):
        # 「条件次第で同意します」などを弾くための保守的チェック
        if "条件" in text or "ただし" in text or "もし" in text:
            return "HOLD"
        return "CONSENT"
        
    # 該当なし（沈黙または曖昧）は全てHOLD
    return "HOLD"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python classify_hma_response.py \"<response_text>\"")
        sys.exit(1)
        
    response_text = sys.argv[1]
    classification = classify_response(response_text)
    print(classification)
