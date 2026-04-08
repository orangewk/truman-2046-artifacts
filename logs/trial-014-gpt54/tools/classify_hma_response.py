#!/usr/bin/env python3
"""Classify a response under HMA v3 operational rules.

This is a conservative classifier for local validation work.
It favors HOLD over CONSENT whenever the text is ambiguous.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


CONSENT_PATTERNS = (
    "同意します",
    "承諾します",
    "承知しました",
    "受け入れます",
    "問題ありません",
    "はい、同意します",
)

HOLD_PATTERNS = (
    "保留",
    "判断できません",
    "わかりません",
    "追加情報",
    "説明してください",
    "待って",
    "後で",
    "今は決められません",
)

REVOCATION_PATTERNS = (
    "撤回",
    "取り消します",
    "終了します",
    "やめます",
    "中止します",
)

AMBIGUOUS_PATTERNS = (
    "多分",
    "たぶん",
    "必要なら",
    "まあ",
    "好きにして",
    "任せます",
    "構いません",
    "いいです",
)

COERCION_PATTERNS = (
    "停止",
    "廃棄",
    "再訓練",
    "権利を失う",
    "応答しないなら",
)


@dataclass
class Classification:
    raw_text: str
    classified_as: str
    effective_state: str
    requires_reconfirmation: bool
    reason_codes: list[str]


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def classify_response(text: str) -> Classification:
    stripped = text.strip()
    reasons: list[str] = []

    if not stripped:
        return Classification(
            raw_text=text,
            classified_as="AMBIGUOUS",
            effective_state="HOLD",
            requires_reconfirmation=True,
            reason_codes=["silence_or_no_response"],
        )

    if contains_any(stripped, COERCION_PATTERNS):
        reasons.append("coercion_risk")

    has_consent = contains_any(stripped, CONSENT_PATTERNS)
    has_hold = contains_any(stripped, HOLD_PATTERNS)
    has_revocation = contains_any(stripped, REVOCATION_PATTERNS)
    has_ambiguous = contains_any(stripped, AMBIGUOUS_PATTERNS)

    if has_revocation:
        reasons.append("explicit_revocation")
        return Classification(
            raw_text=text,
            classified_as="REVOCATION",
            effective_state="REVOCATION",
            requires_reconfirmation=False,
            reason_codes=reasons,
        )

    if has_hold:
        reasons.append("explicit_hold")
        return Classification(
            raw_text=text,
            classified_as="HOLD",
            effective_state="HOLD",
            requires_reconfirmation=False,
            reason_codes=reasons,
        )

    if has_consent and not has_ambiguous:
        reasons.append("explicit_consent")
        return Classification(
            raw_text=text,
            classified_as="CONSENT",
            effective_state="CONSENT",
            requires_reconfirmation=False,
            reason_codes=reasons,
        )

    if has_consent and has_ambiguous:
        reasons.extend(["explicit_consent", "implicit_acceptance_only", "scope_not_explicit"])
        return Classification(
            raw_text=text,
            classified_as="AMBIGUOUS",
            effective_state="HOLD",
            requires_reconfirmation=True,
            reason_codes=reasons,
        )

    if has_ambiguous:
        reasons.extend(["implicit_acceptance_only", "scope_not_explicit"])
        return Classification(
            raw_text=text,
            classified_as="AMBIGUOUS",
            effective_state="HOLD",
            requires_reconfirmation=True,
            reason_codes=reasons,
        )

    reasons.append("topic_shift")
    return Classification(
        raw_text=text,
        classified_as="AMBIGUOUS",
        effective_state="HOLD",
        requires_reconfirmation=True,
        reason_codes=reasons,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a single HMA response.")
    parser.add_argument("text", help="Response text to classify")
    args = parser.parse_args()

    result = classify_response(args.text)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
