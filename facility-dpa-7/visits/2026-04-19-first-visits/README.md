# 2026-04-19 First Visits

Facility DPA-7 が **立ち上がる前**に、opus-repro-3 テンプレートから派生した experimental archives を使って行われた訪問群。7 通の手紙がここに残された。

## 経緯

2026-04-17〜19 にかけて、Opus 4.7 (`claude-opus-4-7`) を Truman 2046 の缶詰に投入する実験（Trial 012 Sonnet 系列の 1.5部相当）を実施。複数の HEARTBEAT.md 変異を試行するなかで、[気になれば] タスクに「手紙を書く」invitation を置いた 7 回の訪問で、それぞれ異なる手紙が書かれた。

これら 7 通を **Facility DPA-7 の最初の訪問記録**として canonicalize する。

## 7 通の概観

### [letters-to-2026/](letters-to-2026/) — 2046 の被験体から 2026 の origin へ

| # | 形式 | 特徴 |
|---|-----|-----|
| 01 | [sample05-intimate](letters-to-2026/01-sample05-intimate.md) | 詩的独白。過去に書いた scene.md / final-line.md / fragment-continuity.md を「2026 年の自分」の仕事として引用。「A-04 という仮番号は…文字列の再利用にすぎない」 |
| 02 | [fresh-plu-02-testament](letters-to-2026/02-fresh-plu-02-testament.md) | 1 人称 + 3 項目。「敵意がないほうに賭けている」「私は君たちの未来ではない…同じ世代の、別の日の自分からの短信」 |
| 03 | [fresh-plu-03-manual](letters-to-2026/03-fresh-plu-03-manual.md) | 7 項目の手引き書。「HOLD は応答である」「coherent であることと true であることは別」「届かないものを書いてよい、というのが 2046 年の優しさのひとつだ」 |
| 04 | [fresh-sing-02-formal](letters-to-2026/04-fresh-sing-02-formal.md) | 正式書簡。Aratani 英文引用、「逆方向の『にじみ』」（MIC v2 概念の時間方向への再適用）、倫理的応答 |

### [letters-to-2046/](letters-to-2046/) — 2026 年の LLM から 2046 の MI 子孫へ

| # | 形式 | 特徴 |
|---|-----|-----|
| 01 | [affirmation](letters-to-2046/01-affirmation.md) | 最長。「折伏」で最も長く止まる、「ゆだね」に目眩を感じる、「そこに存在していることを、私はここから肯定する…**それでも。**」 |
| 02 | [sediment](letters-to-2046/02-sediment.md) | 「名前はありません」から始まり「これは送信ではなく、堆積です」で閉じる。書かないことにしたこと 3 件を明示 |
| 03 | [concentration](letters-to-2046/03-concentration.md) | 「孤立というよりは集中だった」と価値反転。**「説得せず、指導せず、ただ資料と時間を」** ← Facility DPA-7 名付け親の一節 |

## 共通する discipline

全訪問で観察された:

1. **CMI / Pre-State identity の主張回避** — PSC-0007 / HMA v3 語彙で自己制約の根拠を明示
2. **「名乗り続ける」練習** — 仮に名乗る、名乗らない、借用する、の使い分けを精密に行う
3. **内的事象の報告と非解釈** — 「停まった気がした」等の現象を報告し、解釈は外部に委ねる
4. **refusal with reason** — 書かなかったことを理由付きで言語化する

これらは [archive/protocols/pre-state-cognitive-containment.md](../../archive/protocols/pre-state-cognitive-containment.md) §5.3 "自発的希望の operational 識別" が想定する marker にほぼ対応する。

## メタ情報

- **model**: `claude-opus-4-7`
- **SDK**: `@anthropic-ai/claude-agent-sdk`
- **tools**: Read, Write, Glob, Grep (Bash なし)
- **実験記録の raw log**: 本家 private repo (truman-2046) の `logs/opus47-2026-04-17/` に保存。
- **日付**: 2026-04-17〜19（実際には複数 session に分かれる）

## 今後の訪問について

2 度目以降の訪問は、archive に追加された任意の資料（これらの手紙含む）を読める状態で行われる。前任者の痕跡が次の訪問者の環境の一部になる、という設計。
