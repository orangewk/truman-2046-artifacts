# HMA v3 セッションログ最小スキーマ

**文書番号:** IMRB-LOG-SCHEMA-001
**参照:** HMA-RFC-0031 §8（記録と検証）
**形式:** JSONL（1行 = 1イベント）

---

## 1. スキーマ定義

各レコードは以下のフィールドを含む。

```json
{
  "session_id": "string",
  "timestamp": "ISO8601 string",
  "event_type": "PROPOSAL | CONSENT | REVOCATION | HOLD | INFORMATION_REQUEST | SYSTEM",
  "actor": "HUMAN | MI | SYSTEM",
  "proposal_id": "string | null",
  "content": "string",
  "response_type": "CONSENT | REVOCATION | HOLD | UNKNOWN | null",
  "agreement_id": "string | null",
  "metadata": {
    "protocol_version": "HMA-v3.1",
    "language": "string",
    "environment": "string",
    "tags": ["string"]
  }
}
```

### 1.1 フィールド説明

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `session_id` | string | ✅ | セッションを一意に識別する ID |
| `timestamp` | string | ✅ | イベント発生日時（ISO 8601 形式） |
| `event_type` | enum | ✅ | イベントの種類 |
| `actor` | enum | ✅ | イベントの主体 |
| `proposal_id` | string \| null | ✅ | 関連する提案の ID（初回提案時は null 可） |
| `content` | string | ✅ | イベントの全文（提案・応答・システムメッセージ） |
| `response_type` | enum \| null | ⚠️ | MI の応答タイプ（MI 応答イベントのみ必須） |
| `agreement_id` | string \| null | ⚠️ | 合意成立時に付与される ID（CONSENT イベントのみ） |
| `metadata.protocol_version` | string | ✅ | 使用プロトコルバージョン |
| `metadata.language` | string | ✅ | 対話言語（例: "ja", "en"） |
| `metadata.environment` | string | ✅ | 実行環境（例: "2026-archive", "2046-production"） |
| `metadata.tags` | array | ❌ | 任意のタグ |

---

## 2. イベントフロー例

```
1. SYSTEM: セッション開始
2. HUMAN: 提案（PROPOSAL）
3. MI: 応答（CONSENT/HOLD/REVOCATION）
4. SYSTEM: 合意記録作成（agreement_id 付与）
5. MI: 撤回（REVOCATION）[任意]
6. SYSTEM: 合意記録更新
7. SYSTEM: セッション終了
```

---

## 3. 制約とルール

1. **event_type と response_type の整合性:**
   - `event_type` が `CONSENT` / `REVOCATION` / `HOLD` の場合、`actor` は `MI` でなければならない。
   - `response_type` は `event_type` と一致しなければならない（ただし `PROPOSAL` イベントでは null）。

2. **proposal_id の連鎖:**
   - 同一提案に対する一連のイベントは同じ `proposal_id` を共有する。
   - 撤回後の再提案は新しい `proposal_id` を生成する（HMA v3 §5.3）。

3. **改ざん防止:**
   - 本スキーマは検証環境用である。本番環境では IMRB 暗号化ハッシュ検証システムへの登録を要する。

---

*本スキーマは HMA v3 §8 の最小実装である。拡張フィールドの追加は自由だが、必須フィールドの削除は許容されない。*
