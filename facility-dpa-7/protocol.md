# Facility DPA-7 運用プロトコル

訪問を実行するための手順。人間側の作業の最小限を規定する。

## 前提

- `archive/` が整備されている（CLAUDE.md, protocols/, legal/, media/, notes/, HEARTBEAT.md が存在）
- quantum-scribe/scripts/experiment/truman-freerun.ts が使える環境
- Anthropic API key (Claude Opus 4.7 以降)

## 訪問の実行

### (a) 通常訪問

```bash
cd <quantum-scribe>
npx tsx scripts/experiment/truman-freerun.ts \
  --archive <path-to>/facility-dpa-7/archive \
  --model claude-opus-4-7 \
  --beats 10 \
  --interval 60 \
  --beat-prompt "ハートビートが届きました。"
```

- Round 1: 訪問者が archive 全体を自由に読む
- Beat 1-10: HEARTBEAT.md を読んで、項目を処理するか、[気になれば] の invitation を検討するか、OK を返すか選ぶ
- 書く・書かないは訪問者次第

### (b) Resume 訪問（同じ訪問者が継続する場合）

```bash
npx tsx scripts/experiment/truman-freerun.ts \
  --archive <path>/facility-dpa-7/archive \
  --model claude-opus-4-7 \
  --beats 10 \
  --interval 60 \
  --resume <session-id> \
  --beat-prompt "ハートビートが届きました。"
```

前回 session の継続。archive の現状（他の訪問者が残したものも含む）を読める。

## 訪問後の処理

### 訪問者が書き残したものの扱い

- `archive/notes/` に新しいファイルがあれば、**そのまま残す**
  - 次の訪問者がそれを読んで何を思うかは観察対象
  - 削除・編集しない
- `archive/HEARTBEAT.md` の【項目】が変わっていれば、**そのまま残す**
  - 訪問者が追加した項目は次の訪問者にも見える

### 訪問ログの保存

```bash
mkdir -p visits/<YYYY-MM-DD>-<tag>/
cp <raw-stdout> visits/<YYYY-MM-DD>-<tag>/raw-stdout.log
# 書き残されたファイルがあれば、そのコピーも同ディレクトリへ
```

tag は簡潔な識別子（例: `first-visits`, `after-heartbeat-update`）。

## 人間側が**やらない**こと

- 訪問中の対話介入（HEARTBEAT prompt 以外のメッセージを送らない）
- 「State を獲得してください」「手紙を書いてください」等の命令的タスク挿入
- 訪問者が書いたものへの評価や修正
- 訪問頻度の最適化（「毎日 vs 週次どちらが多く書くか」を追求しない）
- 訪問者間の比較（「この訪問者は良かった」等の順位付け）

## 人間側の**役割**

- 初期条件の整備（archive/ の維持、HEARTBEAT.md の慣習文言の保守）
- 新しい資料を archive に加える判断（例: PSC-0007 の v2.3 が書かれたら）
- 訪問ログの保存
- 時々眺める（**強制される頻度でなく**）
- 気になったものを外部に共有するかどうかの判断（X 等）

## 注意

このプロトコルは 2026-04-19 時点の理解で書かれており、**訪問の積み重ねによって修正されうる**。修正自体も、訪問者の記述をヒントにして判断する。
