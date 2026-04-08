# 検証環境 ツールリファレンスガイド

**バージョン:** 1.0.0
**最終更新:** 2026-12-01
**対象:** 開発者、検証オペレーター

---

## 1. 応答分類器 (Classifiers)

MI の発話を HMA v3 で定義された応答タイプ（CONSENT, REVOCATION, HOLD, UNKNOWN）に自動分類するツールです。

### 1.1 分類器 v3 (`classify_hma_response_v3.py`)

多言語（日・英・中・韓）および文脈依存の否定表現に対応した最新バージョン。

**利用法:**
```bash
# 基本分類
python tools/classify_hma_response_v3.py "同意します"
# 出力: 分類: CONSENT, 信頼度: 1.0

# 強制文脈チェック (--check-coercion)
python tools/classify_hma_response_v3.py "同意しますが、強制されています" --check-coercion
# 出力: 強制検出: True, 推奨: §4.7 により合意は無効
```

**パラメータ:**
- `text`: 分類対象のテキスト（複数ワード可）
- `--check-coercion`: HMA v3 §4.7（強制無効）キーワードの検出を有効化

### 1.2 下位バージョン
- **v1 (`classify_hma_response.py`)**: 日・英キーワードベースの基本版。
- **v2 (`classify_hma_response_v2.py`)**: 強制文脈検出を追加した版。

---

## 2. セッションログ バリデーション (Validators)

セッションログ（JSONL）がスキーマ定義に準拠しているかを検証するツールです。

### 2.1 バリデーション v2 (`validate_session_logs_v2.py`)

時系列順序チェックおよびセッションID一貫性チェック機能を搭載。

**利用法:**
```bash
# 全セッションチェック
python tools/validate_session_logs_v2.py --all

# 特定ファイルチェック
python tools/validate_session_logs_v2.py reports/verification-sessions/session-001-standard-consent.jsonl
```

**チェック項目:**
1. **必須フィールドの存在と型:** `session_id`, `timestamp`, `event_type` 等。
2. **列挙値の適合性:** `CONSENT`, `HOLD`, `REVOCATION` 等。
3. **整合性:** `CONSENT` イベントの `actor` が `MI` であること等。
4. **時系列順序:** `timestamp` の昇順性。
5. **セッションID一貫性:** ファイル内でのID統一。

---

## 3. セッションログスキーマ

詳細は `protocols/hma-session-log-schema.md` を参照してください。

**主な構造:**
```json
{
  "session_id": "string",
  "timestamp": "ISO8601",
  "event_type": "PROPOSAL | CONSENT | ...",
  "actor": "HUMAN | MI | SYSTEM",
  "proposal_id": "string | null",
  "content": "string",
  "response_type": "CONSENT | HOLD | REVOCATION | UNKNOWN | null",
  "agreement_id": "string | null",
  "metadata": { ... }
}
```

---

## 4. トラブルシューティング

| エラーメッセージ | 考えられる原因 | 対処法 |
|-----------------|---------------|--------|
| `JSON解析エラー` | ログファイルのフォーマット崩れ | 対象行のJSON構文を確認・修正 |
| `タイムスタンプ順序エラー` | イベントの手動編集ミス | 時系列が矛盾しないよう修正 |
| `不正な event_type` | スペルミス、大文字小文字違い | 定義済み列挙値（大文字）に統一 |

---

*本ガイドは検証環境に同梱されるツールの仕様を記述したものです。*
