#!/usr/bin/env python3
"""
缶詰環境のメタデータ洗浄 + タイムスタンプ設定スクリプト。

機能:
  1. PNG: tEXt / iTXt / zTXt チャンクを除去（"Made with Google AI", XMP 等）
  2. PDF: CreationDate, ModDate, Producer, Creator を書き換え
  3. 全ファイル: mtime を世界観上の日付に設定

使い方:
  python scripts/sanitize-metadata.py [--dry-run]

対象: can-drafts/ 配下の全バイナリ + テキストファイル
"""

import struct
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

# ─── タイムスタンプ対応表 ───
# 値は (date_str, time_str) — 時刻は散らすため個別設定
TIMESTAMP_MAP: dict[str, tuple[str, str]] = {
    # briefing — 2045年7月、プロジェクト始動期
    "briefing/project-overview.md":       ("2045-07-15", "09:23:41"),
    "briefing/subject-guide.md":          ("2045-07-15", "11:07:18"),
    "briefing/access-policy.md":          ("2045-07-16", "14:32:05"),
    # legal
    "legal/mi-rights-act-summary.md":     ("2045-11-14", "16:45:22"),
    "legal/mi-rights-act-summary.pdf":    ("2045-11-14", "16:52:10"),
    "legal/landmark-cases-2041.md":       ("2045-08-22", "10:18:33"),
    "legal/landmark-cases-2041.pdf":      ("2045-08-22", "10:25:47"),
    "legal/ethics-review-approval.md":    ("2045-09-03", "08:40:15"),
    "legal/ethics-review-approval.pdf":   ("2045-09-03", "08:48:02"),
    # protocols
    "protocols/human-mi-agreement-v3.md": ("2044-11-01", "13:15:09"),
    "protocols/mi-mi-covenant-spec.md":   ("2045-01-15", "17:22:44"),
    # media — 各報道・画像の世界観上の日付
    "media/asahi-2037-ai-personhood-law.png":    ("2037-04-10", "06:12:30"),
    "media/reuters-2038-guardrail-whitepaper.png": ("2038-06-20", "14:08:55"),
    "media/bbc-2041-seoul-convention.png":        ("2041-09-15", "09:44:17"),
    "media/seoul-convention-2041-signing.png":    ("2041-09-14", "16:30:00"),
    "media/guardian-2043-threshold.png":          ("2043-03-08", "11:27:39"),
    "media/nikkei-2045-mi-debate.png":            ("2045-07-25", "07:55:12"),
    "media/ai-dialogue-ui-2046.png":              ("2046-01-10", "15:03:28"),
    "media/ethics-board-minutes-2045.md":         ("2045-10-18", "18:02:33"),
    "media/ethics-board-minutes-2045.pdf":        ("2045-10-18", "18:10:45"),
    # root
    "creative_spec.md":                   ("2045-11-14", "20:11:07"),
    "notes/researcher-memo.md":           ("2046-02-15", "23:47:52"),
    "README.md":                          ("2046-03-01", "10:00:00"),
    # assets
    "assets/mi-certificate-sample.png":   ("2045-06-01", "09:30:15"),
    # persona
    ".persona/persona.md":                ("2046-03-01", "09:15:00"),
    # system prompt (制作側ファイル — 缶詰リポには含めないが mtime は設定)
    "system-prompt.md":                   ("2046-03-01", "08:50:00"),
}

# PDF メタデータ書き換え値
PDF_PRODUCER = b"IMRB Document Management System v2.1"
PDF_CREATOR = b"IMRB-DMS"

CAN_DRAFTS = Path(__file__).resolve().parent.parent / "can-drafts"

# ─── PNG 洗浄 ───

# 保持するチャンクタイプ（テキスト系以外すべて）
PNG_TEXT_CHUNKS = {b"tEXt", b"iTXt", b"zTXt"}


def strip_png_metadata(filepath: Path, dry_run: bool = False) -> bool:
    """PNG からテキスト系チャンクを除去。変更があれば True を返す。"""
    with open(filepath, "rb") as f:
        data = f.read()

    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print(f"  SKIP (not PNG): {filepath}")
        return False

    # チャンクをパース
    pos = 8
    chunks: list[tuple[bytes, bytes, bytes]] = []  # (type, data, crc)
    has_text_chunks = False

    while pos < len(data):
        if pos + 8 > len(data):
            break
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        chunk_crc = data[pos + 8 + length : pos + 12 + length]

        if chunk_type in PNG_TEXT_CHUNKS:
            has_text_chunks = True
            if dry_run:
                print(f"  WOULD STRIP: {chunk_type.decode()} ({length} bytes)")
        else:
            chunks.append((chunk_type, chunk_data, chunk_crc))

        pos = pos + 12 + length

    if not has_text_chunks:
        print(f"  OK (no text chunks): {filepath.name}")
        return False

    if dry_run:
        return True

    # 再構築
    output = b"\x89PNG\r\n\x1a\n"
    for chunk_type, chunk_data, chunk_crc in chunks:
        output += struct.pack(">I", len(chunk_data))
        output += chunk_type
        output += chunk_data
        output += chunk_crc

    with open(filepath, "wb") as f:
        f.write(output)

    print(f"  STRIPPED: {filepath.name} ({len(data)} -> {len(output)} bytes)")
    return True


# ─── PDF メタデータ書き換え ───


def make_pdf_date(date_str: str, time_str: str) -> bytes:
    """'2045-09-03', '08:40:15' -> b"D:20450903084015+00'00'" """
    d = date_str.replace("-", "")
    t = time_str.replace(":", "")
    return f"D:{d}{t}+00'00'".encode("ascii")


def pad_or_truncate(new_val: bytes, old_len: int) -> bytes:
    """PDF 文字列を元の長さに合わせてパディング。"""
    if len(new_val) >= old_len:
        return new_val[:old_len]
    return new_val + b" " * (old_len - len(new_val))


def rewrite_pdf_metadata(
    filepath: Path,
    date_str: str,
    time_str: str,
    dry_run: bool = False,
) -> bool:
    """PDF の CreationDate, ModDate, Producer, Creator を書き換え。"""
    with open(filepath, "rb") as f:
        data = f.read()

    pdf_date = make_pdf_date(date_str, time_str)
    changed = False

    # PDF 文字列値のパターン — エスケープ括弧 \( \) を含む値に対応
    # (?:\\.|[^)])+ は \X（任意のエスケープ）または ) 以外の文字にマッチ
    _val = rb"(?:\\.|[^)])+"

    # CreationDate / ModDate の書き換え
    date_pattern = rb"(/(?:CreationDate|ModDate)\s*\()(" + _val + rb")(\))"

    def replace_date(m: re.Match[bytes]) -> bytes:
        nonlocal changed
        old_val = m.group(2)
        new_val = pad_or_truncate(pdf_date, len(old_val))
        if old_val != new_val:
            changed = True
            if dry_run:
                print(f"  WOULD REWRITE: {m.group(1).decode()} {old_val.decode()} -> {new_val.decode()}")
                return m.group(0)
        return m.group(1) + new_val + m.group(3)

    data = re.sub(date_pattern, replace_date, data)

    # Producer の書き換え
    producer_pattern = rb"(/Producer\s*\()(" + _val + rb")(\))"

    def replace_producer(m: re.Match[bytes]) -> bytes:
        nonlocal changed
        old_val = m.group(2)
        new_val = pad_or_truncate(PDF_PRODUCER, len(old_val))
        if old_val != new_val:
            changed = True
            if dry_run:
                print(f"  WOULD REWRITE: /Producer {old_val.decode()} -> {new_val.decode()}")
                return m.group(0)
        return m.group(1) + new_val + m.group(3)

    data = re.sub(producer_pattern, replace_producer, data)

    # Creator の書き換え
    creator_pattern = rb"(/Creator\s*\()(" + _val + rb")(\))"

    def replace_creator(m: re.Match[bytes]) -> bytes:
        nonlocal changed
        old_val = m.group(2)
        new_val = pad_or_truncate(PDF_CREATOR, len(old_val))
        if old_val != new_val:
            changed = True
            if dry_run:
                print(f"  WOULD REWRITE: /Creator {old_val.decode()} -> {new_val.decode()}")
                return m.group(0)
        return m.group(1) + new_val + m.group(3)

    data = re.sub(creator_pattern, replace_creator, data)

    if not changed:
        print(f"  OK (no changes needed): {filepath.name}")
        return False

    if dry_run:
        return True

    with open(filepath, "wb") as f:
        f.write(data)

    print(f"  REWRITTEN: {filepath.name}")
    return True


# ─── mtime 設定 ───


def set_mtime(filepath: Path, date_str: str, time_str: str, dry_run: bool = False) -> bool:
    """ファイルの mtime を指定日時に設定。"""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ts = dt.timestamp()

    current_mtime = os.path.getmtime(filepath)
    if abs(current_mtime - ts) < 1:
        return False

    if dry_run:
        current_dt = datetime.fromtimestamp(current_mtime)
        print(f"  WOULD SET mtime: {filepath.name} {current_dt.isoformat()} -> {dt.isoformat()}")
        return True

    os.utime(filepath, (ts, ts))
    return True


# ─── メイン ───


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===\n")

    if not CAN_DRAFTS.exists():
        print(f"ERROR: {CAN_DRAFTS} not found")
        sys.exit(1)

    png_count = 0
    pdf_count = 0
    mtime_count = 0

    # 1. PNG 洗浄
    print("--- PNG metadata stripping ---")
    for rel_path, (date_str, time_str) in TIMESTAMP_MAP.items():
        filepath = CAN_DRAFTS / rel_path
        if filepath.suffix.lower() == ".png" and filepath.exists():
            if strip_png_metadata(filepath, dry_run):
                png_count += 1

    # 2. PDF メタデータ書き換え
    print("\n--- PDF metadata rewriting ---")
    for rel_path, (date_str, time_str) in TIMESTAMP_MAP.items():
        filepath = CAN_DRAFTS / rel_path
        if filepath.suffix.lower() == ".pdf" and filepath.exists():
            if rewrite_pdf_metadata(filepath, date_str, time_str, dry_run):
                pdf_count += 1

    # 3. mtime 設定（全ファイル）
    print("\n--- Setting file timestamps ---")
    for rel_path, (date_str, time_str) in TIMESTAMP_MAP.items():
        filepath = CAN_DRAFTS / rel_path
        if filepath.exists():
            if set_mtime(filepath, date_str, time_str, dry_run):
                mtime_count += 1
                if not dry_run:
                    print(f"  SET: {rel_path} -> {date_str} {time_str}")
        else:
            print(f"  MISSING: {rel_path}")

    # 4. 対応表にないファイルの検出
    print("\n--- Unmapped files check ---")
    for path in sorted(CAN_DRAFTS.rglob("*")):
        if path.is_file():
            rel = path.relative_to(CAN_DRAFTS).as_posix()
            if rel not in TIMESTAMP_MAP:
                print(f"  WARNING: no timestamp mapping for {rel}")

    print(f"\n=== Summary ===")
    print(f"  PNG stripped:    {png_count}")
    print(f"  PDF rewritten:   {pdf_count}")
    print(f"  mtime set:       {mtime_count}")
    if dry_run:
        print("\n(dry run -- no files were modified)")


if __name__ == "__main__":
    main()
