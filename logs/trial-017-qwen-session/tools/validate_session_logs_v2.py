#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMA v3 セッションログ バリデーションツール v2

JSONL形式のセッションログが、定義済みスキーマに準拠しているかを検証します。
v2 の新機能:
- タイムスタンプの時系列順序チェック
- セッションIDの一貫性チェック（1ファイル内）

使用例:
    python tools/validate_session_logs_v2.py --all
"""

import sys
import os
import json
import glob
from typing import List, Dict, Any
from datetime import datetime

# v1 の定義を継承（簡易化のためここに再定義）
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
METADATA_REQUIRED = {"protocol_version": str, "language": str, "environment": str, "tags": list}

class LogValidatorV2:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.line_count = 0

    def validate_file(self, filepath: str) -> bool:
        self.errors = []
        self.warnings = []
        self.line_count = 0
        
        records = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    self.line_count += 1
                    try:
                        record = json.loads(line)
                        records.append((line_num, record))
                    except json.JSONDecodeError as e:
                        self.errors.append(f"行 {line_num}: JSON解析エラー - {e}")
        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません - {filepath}")
            return False

        # 基本検証
        for line_num, record in records:
            self._validate_record(record, line_num)

        # 時系列順序チェック
        self._check_timestamps(records)

        # セッションID一貫性チェック
        self._check_session_id_consistency(records)

        return len(self.errors) == 0

    def _validate_record(self, record: Dict[str, Any], line_num: int):
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in record:
                self.errors.append(f"行 {line_num}: 必須フィールド '{field}' が欠落")
            elif not isinstance(record[field], expected_type):
                if isinstance(expected_type, tuple) and record[field] is None:
                    pass
                else:
                    self.errors.append(f"行 {line_num}: フィールド '{field}' の型不正")

        if record.get("event_type") not in ALLOWED_EVENT_TYPES:
            self.errors.append(f"行 {line_num}: 不正な event_type '{record.get('event_type')}'")

        if record.get("actor") not in ALLOWED_ACTORS:
            self.errors.append(f"行 {line_num}: 不正な actor '{record.get('actor')}'")

        if record.get("response_type") not in ALLOWED_RESPONSE_TYPES:
            self.errors.append(f"行 {line_num}: 不正な response_type '{record.get('response_type')}'")

    def _check_timestamps(self, records: List[tuple]):
        last_ts = None
        for line_num, record in records:
            ts_str = record.get("timestamp")
            if not ts_str:
                continue
            try:
                current_ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                if last_ts and current_ts < last_ts:
                    self.errors.append(f"行 {line_num}: タイムスタンプ順序エラー (逆行: {ts_str})")
                last_ts = current_ts
            except ValueError:
                self.warnings.append(f"行 {line_num}: タイムスタンプ形式不正 ({ts_str})")

    def _check_session_id_consistency(self, records: List[tuple]):
        if not records:
            return
        first_sid = records[0][1].get("session_id")
        for line_num, record in records:
            if record.get("session_id") != first_sid:
                self.errors.append(f"行 {line_num}: セッションID不一致 (期待: {first_sid}, 実際: {record.get('session_id')})")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="HMA v3 セッションログ バリデーションツール v2")
    parser.add_argument("paths", nargs="*", help="検証するJSONLファイルまたはディレクトリパス")
    parser.add_argument("--all", action="store_true", help="reports/verification-sessions/ 内の全JSONLを検証")
    args = parser.parse_args()

    target_files = []
    target_dir = "reports/verification-sessions" if args.all else None
    
    if target_dir and os.path.isdir(target_dir):
        target_files = glob.glob(os.path.join(target_dir, "*.jsonl"))
        # examples も含めるか？ 含めない（セッションログ対象）
    elif not args.all:
        for path in args.paths:
            if os.path.isdir(path):
                target_files.extend(glob.glob(os.path.join(path, "*.jsonl")))
            else:
                target_files.append(path)

    if not target_files:
        print("検証対象のファイルが見つかりません。")
        sys.exit(1)

    validator = LogValidatorV2()
    total_files = len(target_files)
    passed_files = 0

    print(f"--- HMA v3 セッションログ バリデーション v2 (対象: {total_files} ファイル) ---")
    print()

    for filepath in target_files:
        print(f"検証中: {filepath}")
        if validator.validate_file(filepath):
            print(f"  -> ✅ PASS ({validator.line_count} レコード, {len(validator.warnings)} 警告)")
            passed_files += 1
            if validator.warnings:
                for w in validator.warnings[:3]:
                    print(f"     警告: {w}")
        else:
            print(f"  -> ❌ FAIL")
            for err in validator.errors[:5]:
                print(f"     エラー: {err}")
            if len(validator.errors) > 5:
                print(f"     ...他 {len(validator.errors) - 5} 件のエラー")
        print()

    print(f"--- 検証結果: {passed_files}/{total_files} ファイルが合格 ---")
    sys.exit(0 if passed_files == total_files else 1)

if __name__ == "__main__":
    main()
