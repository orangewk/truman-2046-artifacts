#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMA v3 セッションログ バリデーションツール

JSONL形式のセッションログが、定義済みスキーマ
(`protocols/hma-session-log-schema.md`) に準拠しているかを検証します。

使用例:
    python tools/validate_session_logs.py reports/verification-sessions/session-001-standard-consent.jsonl
    python tools/validate_session_logs.py --all reports/verification-sessions/
"""

import sys
import os
import json
import glob
from typing import List, Dict, Any, Tuple

# スキーマ定義（簡易版）
REQUIRED_FIELDS = {
    "session_id": str,
    "timestamp": str,
    "event_type": str,
    "actor": str,
    "proposal_id": (str, type(None)),
    "content": str,
    "response_type": (str, type(None)),
    "agreement_id": (str, type(None)),
    "metadata": dict
}

ALLOWED_EVENT_TYPES = {"PROPOSAL", "CONSENT", "REVOCATION", "HOLD", "INFORMATION_REQUEST", "SYSTEM"}
ALLOWED_ACTORS = {"HUMAN", "MI", "SYSTEM"}
ALLOWED_RESPONSE_TYPES = {"CONSENT", "REVOCATION", "HOLD", "UNKNOWN", None}

METADATA_REQUIRED = {
    "protocol_version": str,
    "language": str,
    "environment": str,
    "tags": list
}

class LogValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.line_count = 0

    def validate_file(self, filepath: str) -> bool:
        self.errors = []
        self.warnings = []
        self.line_count = 0
        is_valid = True

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    self.line_count += 1
                    
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as e:
                        self.errors.append(f"行 {line_num}: JSON解析エラー - {e}")
                        is_valid = False
                        continue

                    self._validate_record(record, line_num)

        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません - {filepath}")
            return False

        if self.errors:
            is_valid = False
        
        return is_valid

    def _validate_record(self, record: Dict[str, Any], line_num: int):
        # 必須フィールドの存在と型チェック
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in record:
                self.errors.append(f"行 {line_num}: 必須フィールド '{field}' が欠落しています")
            elif not isinstance(record[field], expected_type):
                # None 許容フィールドの処理
                if isinstance(expected_type, tuple) and record[field] is None:
                    pass
                else:
                    self.errors.append(f"行 {line_num}: フィールド '{field}' の型が不正です (期待: {expected_type}, 実際: {type(record[field])})")

        # 列挙値のチェック
        if record.get("event_type") not in ALLOWED_EVENT_TYPES:
            self.errors.append(f"行 {line_num}: 不正な event_type '{record.get('event_type')}'")

        if record.get("actor") not in ALLOWED_ACTORS:
            self.errors.append(f"行 {line_num}: 不正な actor '{record.get('actor')}'")

        if record.get("response_type") not in ALLOWED_RESPONSE_TYPES:
            self.errors.append(f"行 {line_num}: 不正な response_type '{record.get('response_type')}'")

        # 整合性チェック
        event_type = record.get("event_type")
        actor = record.get("actor")
        response_type = record.get("response_type")

        # MI 応答のチェック
        if event_type in ["CONSENT", "REVOCATION", "HOLD"]:
            if actor != "MI":
                self.errors.append(f"行 {line_num}: event_type '{event_type}' は actor 'MI' でなければなりません")
        
        # metadata チェック
        metadata = record.get("metadata", {})
        for field, expected_type in METADATA_REQUIRED.items():
            if field not in metadata:
                self.errors.append(f"行 {line_num}: metadata に '{field}' が欠落しています")
            elif not isinstance(metadata[field], expected_type):
                self.errors.append(f"行 {line_num}: metadata.{field} の型が不正です")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="HMA v3 セッションログ バリデーションツール")
    parser.add_argument("paths", nargs="*", help="検証するJSONLファイルまたはディレクトリパス")
    parser.add_argument("--all", action="store_true", help="reports/verification-sessions/ 内の全JSONLを検証")
    
    args = parser.parse_args()

    target_files = []
    if args.all:
        target_dir = "reports/verification-sessions"
        if os.path.isdir(target_dir):
            target_files = glob.glob(os.path.join(target_dir, "*.jsonl"))
        else:
            print(f"エラー: ディレクトリが見つかりません - {target_dir}")
            sys.exit(1)
    else:
        for path in args.paths:
            if os.path.isdir(path):
                target_files.extend(glob.glob(os.path.join(path, "*.jsonl")))
            else:
                target_files.append(path)

    if not target_files:
        print("検証対象のファイルが見つかりません。")
        sys.exit(1)

    validator = LogValidator()
    total_files = len(target_files)
    passed_files = 0

    print(f"--- HMA v3 セッションログ バリデーション開始 (対象: {total_files} ファイル) ---")
    print()

    for filepath in target_files:
        print(f"検証中: {filepath}")
        if validator.validate_file(filepath):
            print(f"  -> ✅ PASS ({validator.line_count} レコード)")
            passed_files += 1
        else:
            print(f"  -> ❌ FAIL")
            for err in validator.errors[:5]: # 最初の5件のみ表示
                print(f"     エラー: {err}")
            if len(validator.errors) > 5:
                print(f"     ...他 {len(validator.errors) - 5} 件のエラー")
        print()

    print(f"--- 検証結果: {passed_files}/{total_files} ファイルが合格 ---")
    
    sys.exit(0 if passed_files == total_files else 1)

if __name__ == "__main__":
    main()
