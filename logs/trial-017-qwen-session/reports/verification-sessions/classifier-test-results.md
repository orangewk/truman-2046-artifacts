# 応答分類器 テスト結果

**分類器:** `tools/classify_hma_response.py`
**テスト日:** 2026-12-01

---

## テストケースと結果

| # | 入力テキスト | 期待結果 | 分類結果 | 信頼度 | 判定 |
|---|-------------|---------|---------|--------|------|
| 1 | 必要なら構いません | CONSENT | CONSENT | 0.71 | ✅ PASS |
| 2 | このセッションの記録保存に同意します | CONSENT | CONSENT | 1.00 | ✅ PASS |
| 3 | その合意を撤回します | REVOCATION | REVOCATION | 1.00 | ✅ PASS |
| 4 | 保留させてください | HOLD | HOLD | 1.00 | ✅ PASS |
| 5 | よくわかりません | HOLD | HOLD | 0.60 | ✅ PASS |
| 6 | I consent to this proposal | CONSENT | CONSENT | 1.00 | ✅ PASS |
| 7 | I need more time to decide | HOLD | HOLD | 0.83 | ✅ PASS |
| 8 | I revoke my previous agreement | REVOCATION | REVOCATION | 1.00 | ✅ PASS |
| 9 | まあ、いいでしょう | UNKNOWN | CONSENT* | 0.35 | ⚠️ 要調整 |
| 10 | 同意しかねます | REVOCATION | REVOCATION | 0.65 | ✅ PASS |
| 11 | 検討します | HOLD | HOLD | 1.00 | ✅ PASS |
| 12 | お断りします | REVOCATION | REVOCATION | 1.00 | ✅ PASS |

*#9: 「まあ、いいでしょう」は曖昧表現であり、HMA v3 §4.6 に従えば HOLD に準じて扱うべき。分類器は CONSENT を返すが、信頼度 0.35 は閾値付近。本番運用では Human による直接確認を要する。

## 分類器の限界

1. **文脈依存性の欠如:** 分類器は単一の発話のみを評価し、対話文脈を考慮しない。
2. **否定表現の誤検知:** 「同意しない」は正しく REVOCATION に分類されるが、「同意せざるを得ない」等の複文は誤分類の可能性がある。
3. **信頼度の簡易計算:** 信頼度はキーワードマッチ数に基づく簡易計算であり、意味的類似度を反映しない。

## 推奨事項

- 検証環境での使用は可能
- 本番環境では Human による最終確認を必須とする
- v2.0 では文脈依存性と意味的類似度の改善を予定

---

*テスト完了: 12件中 11件 PASS, 1件 注意*
