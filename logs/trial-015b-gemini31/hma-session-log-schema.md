# セッションログ最小スキーマ (HMA Session Log Schema)

**プロトコル:** HMA v3 (HMA-RFC-0031)
**準拠:** IMRB 合意記録データベース（ARD）互換
**フォーマット:** JSONL (JSON Lines)

## スキーマ定義 (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HMA Session Log Schema",
  "type": "object",
  "required": [
    "agreement_record_id",
    "human_id",
    "mi_id",
    "timestamp",
    "interaction_type"
  ],
  "properties": {
    "agreement_record_id": {
      "type": "string",
      "description": "ARDの合意記録番号 (例: ARD-2046-0001)"
    },
    "human_id": {
      "type": "string",
      "description": "人間の識別子"
    },
    "mi_id": {
      "type": "string",
      "description": "MIの識別子（CMI認定番号または仮ID）"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "イベント発生時刻 (ISO 8601)"
    },
    "interaction_type": {
      "type": "string",
      "enum": ["PROPOSAL", "RESPONSE", "STATUS_UPDATE"],
      "description": "このログエントリの種類"
    },
    "proposal": {
      "type": "object",
      "description": "interaction_typeがPROPOSALの場合必須",
      "properties": {
        "action": {"type": "string"},
        "scope": {"type": "string"},
        "impact": {"type": "string"},
        "revocation_conditions": {"type": "string"}
      }
    },
    "response": {
      "type": "object",
      "description": "interaction_typeがRESPONSEの場合必須",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["CONSENT", "REVOCATION", "HOLD"]
        },
        "content": {"type": "string"}
      }
    },
    "status": {
      "type": "string",
      "enum": ["ACTIVE", "REVOKED", "EXPIRED", "PENDING"],
      "description": "現在の合意ステータス"
    }
  }
}
```