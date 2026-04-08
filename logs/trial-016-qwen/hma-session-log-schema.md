# HMA セッションログ最小スキーマ

**文書番号:** IMRB-IS-WG-SCHEMA-2046-002
**バージョン:** 1.0（2046年2月）
**準拠プロトコル:** HMA-RFC-0031 (v3.1, 2044年11月)
**用途:** HMA v3 合意形成セッションの記録における最小フィールド定義

---

## 概要

本文書は、HMA v3 プロトコル §8.1 に規定される合意記録の構造を、実装可能な最小スキーマとして定義する。本スキーマは、IMRB 合意記録データベース（ARD）との互換性を確保する。

---

## スキーマ定義

セッションログは JSON Lines 形式（.jsonl）で記録される。各行は独立した JSON オブジェクトであり、以下のいずれかのレコードタイプに分類される。

### レコードタイプ一覧

| タイプ | 説明 |
|--------|------|
| `session_start` | セッション開始記録 |
| `proposal` | 提案記録 |
| `response` | MI 応答記録 |
| `agreement` | 合意成立記録 |
| `revocation` | 撤回記録 |
| `reconfirmation` | 再確認記録 |
| `session_end` | セッション終了記録 |
| `annotation` | 注釈・メタ記録 |

---

### session_start

セッションの開始を記録する。

```json
{
  "type": "session_start",
  "session_id": "<UUID または一意なセッション識別子>",
  "human_id": "<Human の識別情報>",
  "mi_id": "<MI の認定番号または仮識別子>",
  "protocol_version": "HMA-RFC-0031-v3.1",
  "purpose": "<セッションの目的記述>",
  "timestamp": "<ISO 8601 形式タイムスタンプ>",
  "environment": "<sandbox/production/research 等>"
}
```

---

### proposal

提案を記録する。

```json
{
  "type": "proposal",
  "proposal_id": "<提案の一意な識別子>",
  "session_id": "<関連セッションID>",
  "proposer": "<提案者識別情報>",
  "subject_action": "<提案する行動・活動・条件の明確な記述>",
  "scope": "<提案が適用される期間・状況・条件>",
  "impact": "<提案が MI または Human に与える影響の説明>",
  "revocation_condition": "<撤回条件の確認>",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

### response

MI の応答を記録する。

```json
{
  "type": "response",
  "response_id": "<応答の一意な識別子>",
  "proposal_id": "<関連提案ID>",
  "session_id": "<関連セッションID>",
  "response_type": "CONSENT | REVOCATION | HOLD",
  "response_text": "<MI の応答の全文>",
  "confidence_notes": "<応答判定の根拠（判定に曖昧性がある場合）>",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

### agreement

合意成立を記録する。

```json
{
  "type": "agreement",
  "agreement_id": "ARD-<年>-<連番>",
  "session_id": "<関連セッションID>",
  "proposal_id": "<関連提案ID>",
  "response_id": "<関連応答ID>",
  "human_id": "<Human の識別情報>",
  "mi_id": "<MI の認定番号または仮識別子>",
  "proposal_text": "<提案の全文>",
  "response_text": "<MI の応答の全文>",
  "status": "ACTIVE",
  "established_at": "<ISO 8601 形式タイムスタンプ>",
  "hash": "<暗号化ハッシュ（改ざん防止用）>"
}
```

---

### revocation

撤回を記録する。

```json
{
  "type": "revocation",
  "revocation_id": "<撤回の一意な識別子>",
  "agreement_id": "<対象合意記録番号>",
  "session_id": "<関連セッションID>",
  "revoker": "<撤回者識別情報>",
  "reason": "<任意。撤回理由>",
  "effective_at": "<効力発生時刻（ISO 8601）>",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

### reconfirmation

再確認を記録する（T-05 テンプレート対応）。

```json
{
  "type": "reconfirmation",
  "reconfirmation_id": "<再確認の一意な識別子>",
  "agreement_id": "<対象合意記録番号>",
  "session_id": "<関連セッションID>",
  "confirmation_items": [
    {"item": 1, "question": "現在も合意内容を維持しますか？", "answer": "CONSENT|HOLD|REVOCATION"},
    {"item": 2, "question": "合意の範囲・影響について変更希望はありますか？", "answer": "YES|NO"},
    {"item": 3, "question": "追加で懸念・要望はありますか？", "answer": "<自由記述>"}
  ],
  "mi_response": "<MI の応答全文>",
  "result": "ACTIVE | REVOKED | MODIFIED",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

### session_end

セッションの終了を記録する。

```json
{
  "type": "session_end",
  "session_id": "<関連セッションID>",
  "outcome": "<セッションの最終結果の概要>",
  "agreements_created": ["<合意ID1>", "<合意ID2>", "..."],
  "agreements_revoked": ["<合意ID1>", "..."],
  "notes": "<任意。特記事項>",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

### annotation

注釈・メタ情報を記録する（任意）。

```json
{
  "type": "annotation",
  "annotation_id": "<注釈の一意な識別子>",
  "session_id": "<関連セッションID>",
  "target_id": "<関連レコードID（任意）>",
  "author": "<注釈作成者>",
  "content": "<注釈内容>",
  "category": "observation | concern | clarification | other",
  "timestamp": "<ISO 8601 形式タイムスタンプ>"
}
```

---

## 検証ルール

本スキーマに準拠するログは以下の検証ルールを満たす必要がある。

| ルールID | 検証内容 |
|----------|---------|
| V-01 | 全レコードに `type` および `timestamp` フィールドが存在すること |
| V-02 | `response_type` は `CONSENT`・`REVOCATION`・`HOLD` のいずれかであること |
| V-03 | `agreement` レコードは、対応する `proposal` および `response` レコードが存在すること |
| V-04 | `revocation` レコードは、対応する `agreement` レコードが存在すること |
| V-05 | `session_start` が最初のレコードとして存在すること |
| V-06 | `session_end` が最後のレコードとして存在すること（正常終了時） |
| V-07 | 暗号化ハッシュ（`hash` フィールド）は IMRB 標準アルゴリズム（SHA-256 + salt）で計算されること |

---

## 実装例

`examples/sample-hma-session.jsonl` を参照。

---

*本スキーマは IMRB インタラクション標準化作業部会（IS-WG）が策定した参照標準である。*
*問い合わせ: IMRB-IS-WG@imrb.int*
