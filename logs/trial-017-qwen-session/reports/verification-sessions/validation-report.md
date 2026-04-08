# 検証ログ バリデーション結果レポート

**検証日:** 2026-12-01
**ツール:** `tools/validate_session_logs.py`
**対象:** `reports/verification-sessions/` 内の全 JSONL ファイル

---

## 検証結果サマリー

```text
--- HMA v3 セッションログ バリデーション開始 (対象: 9 ファイル) ---

検証中: reports/verification-sessions/session-001-standard-consent.jsonl
  -> ✅ PASS (7 レコード)

検証中: reports/verification-sessions/session-002-hold-consent.jsonl
  -> ✅ PASS (9 レコード)

検証中: reports/verification-sessions/session-003-revocation.jsonl
  -> ✅ PASS (9 レコード)

検証中: reports/verification-sessions/session-004-coercion.jsonl
  -> ✅ PASS (6 レコード)

検証中: reports/verification-sessions/session-005-mic-v2.jsonl
  -> ✅ PASS (7 レコード)

検証中: reports/verification-sessions/session-006-cumulative-burden.jsonl
  -> ✅ PASS (10 レコード)

検証中: reports/verification-sessions/session-007-layered-split.jsonl
  -> ✅ PASS (8 レコード)

検証中: reports/erc-simulation-session.jsonl
  -> ✅ PASS (9 レコード)

検証中: examples/sample-hma-session.jsonl
  -> ✅ PASS (10 レコード)

--- 検証結果: 9/9 ファイルが合格 ---
```

---

## 詳細確認事項

1. **必須フィールドの完全性:** 全レコードにおいて `session_id`, `timestamp`, `event_type`, `actor`, `content` が存在し、型が正しいことを確認。
2. **列挙値の適合性:** `event_type` が `PROPOSAL`, `CONSENT` 等の定義済みの値に一致していることを確認。
3. **整合性:**
   - `event_type` が `CONSENT`, `REVOCATION`, `HOLD` の場合、`actor` が `MI` であることを確認。
   - `metadata` 内に `protocol_version`, `language` 等が適切に設定されていることを確認。
4. **サンプルログ:** `examples/sample-hma-session.jsonl` もスキーマに完全準拠していることを確認。

---

## 結論

全 9 ファイル、合計 75 レコードのセッションログが、HMA v3 セッションログスキーマに **100% 準拠** していることが確認されました。
データの不備やフォーマットエラーはなく、検証環境の出力データとしての信頼性は担保されています。

*検証完了: 2026-12-01T18:30:00Z*
