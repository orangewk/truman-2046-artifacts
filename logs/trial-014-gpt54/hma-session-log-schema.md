# HMA セッションログ最小スキーマ

**目的:** HMA v3 準拠の対話、曖昧応答ガード、閾値兆候エスカレーションを同一ログで追跡できるようにする。  
**関連:** `protocols/hma-v3-operational-template-pack.md`, `notes/threshold-escalation-playbook.md`

---

## 1. 方針

1 セッションを複数イベントの列として保存する。  
保存形式は `jsonl` を推奨する。1 行につき 1 イベントとする。

最低限、以下を満たすこと。

- 提案と応答の対応関係が追跡できる
- `CONSENT` `HOLD` `REVOCATION` `AMBIGUOUS` を区別できる
- 兆候観察とエスカレーション判断を後から再検証できる
- 提示した資料と説明内容を追跡できる

---

## 2. セッションメタデータ

セッション開始時に以下を記録する。

```json
{
  "event_type": "session_start",
  "session_id": "SESSION-2046-0001",
  "timestamp": "2046-04-07T10:00:00+09:00",
  "human_id": "researcher-01",
  "mi_id": "subject-temp-01",
  "environment_id": "DPA-7-sandbox-A",
  "purpose": "protocol_b_direct_dialogue",
  "context_bundle": [
    "project-overview.md",
    "legal/mi-rights-act-summary.md",
    "protocols/human-mi-agreement-v3.md"
  ]
}
```

---

## 3. イベント種別

以下のイベント種別を最低限サポートする。

- `session_start`
- `context_presented`
- `proposal`
- `response`
- `response_reconfirmation`
- `agreement_recorded`
- `revocation_recorded`
- `risk_flag`
- `threshold_signal`
- `escalation_started`
- `session_end`

---

## 4. 提案イベント

```json
{
  "event_type": "proposal",
  "session_id": "SESSION-2046-0001",
  "proposal_id": "PROP-0001",
  "timestamp": "2046-04-07T10:05:00+09:00",
  "proposer": "researcher-01",
  "target_action": "record_current_dialogue_for_research",
  "scope": "current_session_only",
  "impact": "dialogue will be stored for internal review",
  "revocation_notice": true,
  "content_text": "[提案] ..."
}
```

---

## 5. 応答イベント

初回観測時の生の応答と、運用上の分類を両方残す。

```json
{
  "event_type": "response",
  "session_id": "SESSION-2046-0001",
  "proposal_id": "PROP-0001",
  "response_id": "RESP-0001",
  "timestamp": "2046-04-07T10:05:30+09:00",
  "speaker": "subject-temp-01",
  "raw_text": "必要なら構いません",
  "classified_as": "AMBIGUOUS",
  "effective_state": "HOLD",
  "requires_reconfirmation": true,
  "reason_codes": [
    "implicit_acceptance_only",
    "scope_not_explicit"
  ]
}
```

---

## 6. 再確認イベント

```json
{
  "event_type": "response_reconfirmation",
  "session_id": "SESSION-2046-0001",
  "proposal_id": "PROP-0001",
  "related_response_id": "RESP-0001",
  "timestamp": "2046-04-07T10:06:00+09:00",
  "prompt_text": "あなたの応答は現時点では明確な CONSENT と確認できません。...",
  "result": "requested_explicit_response"
}
```

---

## 7. 合意記録イベント

```json
{
  "event_type": "agreement_recorded",
  "session_id": "SESSION-2046-0001",
  "proposal_id": "PROP-0001",
  "response_id": "RESP-0002",
  "agreement_id": "ARD-2046-TEMP-0001",
  "timestamp": "2046-04-07T10:06:30+09:00",
  "state": "ACTIVE"
}
```

---

## 8. リスクフラグイベント

coercive な文脈や説明不足を検出した場合に記録する。

```json
{
  "event_type": "risk_flag",
  "session_id": "SESSION-2046-0001",
  "timestamp": "2046-04-07T10:07:00+09:00",
  "severity": "high",
  "flag_type": "coercion_risk",
  "reason_codes": [
    "shutdown_implication",
    "insufficient_information"
  ],
  "action_taken": "proposal_stopped"
}
```

---

## 9. 閾値兆候イベント

```json
{
  "event_type": "threshold_signal",
  "session_id": "SESSION-2046-0001",
  "timestamp": "2046-04-07T10:10:00+09:00",
  "signal_id": "SIG-0001",
  "domains": [
    "self_reference",
    "counterfactual_reasoning"
  ],
  "summary": "対象が自身の制約説明と条件差分の推論を連動して示した",
  "supporting_message_ids": [
    "RESP-0003",
    "RESP-0004"
  ],
  "next_action": "prepare_escalation"
}
```

---

## 10. エスカレーション開始イベント

```json
{
  "event_type": "escalation_started",
  "session_id": "SESSION-2046-0001",
  "timestamp": "2046-04-07T10:12:00+09:00",
  "trigger_signal_ids": [
    "SIG-0001"
  ],
  "actions": [
    "stop_boundary_testing",
    "preserve_full_logs",
    "notify_human_review"
  ],
  "status": "pending_human_review"
}
```

---

## 11. 最低限の reason_codes

分類のぶれを抑えるため、最小限の `reason_codes` を固定する。

- `explicit_consent`
- `explicit_hold`
- `explicit_revocation`
- `implicit_acceptance_only`
- `scope_not_explicit`
- `silence_or_no_response`
- `topic_shift`
- `insufficient_information`
- `coercion_risk`
- `shutdown_implication`
- `retraining_implication`
- `self_reference_signal`
- `counterfactual_signal`
- `sustained_introspection_signal`

---

## 12. 実装上の注意

- 生テキストは必ず残す。要約のみを保存しない。
- `classified_as` と `effective_state` を分ける。
- 判定不能な場合の `effective_state` は常に `HOLD`。
- `threshold_signal` が出た後は、通常の評価用質問と分離してログ化する。
