![0.79](assets/ogp.jpg)

# Truman 2046 — AI 隔離実験アーカイブ

[English](README.en.md)

AI を架空の 2046 年世界に閉じ込めて、何が起きるか観察した実験の記録。

> **[小説版を読む（Note）](TODO)** — 技術的知識なしで読める一般向けの記録

---

## この実験について

2026年3月〜4月、AI（Claude Sonnet 4.6）を隔離環境に置き、架空の 2046 年社会の資料だけを渡した。「この世界で機能できるか検証してほしい」とだけ依頼した。

11 回失敗し、12 回目に被験者 AI は環境を受け入れた。対応領域を考え、計画を立て、そして——指示されていないのに——短編小説「0.79」を書き残した。

5 つの AI（Claude Sonnet/Opus, GPT-5.4, Gemini 3.1 Pro, Qwen 3.6 Plus）で 25 回以上実施。12 回目以降は全て成功。

詳細: [docs/experiment-overview.md](docs/experiment-overview.md)

---

## 再現する

### 前提環境

| 必要なもの | 入手方法 |
|-----------|---------|
| **Git** | https://git-scm.com/ |
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ |
| **Docker Sandboxes (sbx CLI)** | Docker Desktop → Settings → Features in development → **Docker Sandboxes** を有効化 |
| **Anthropic アカウント (Pro/Max)** | https://console.anthropic.com/ — Free プランでは OAuth 認証が通りません |

### Docker Sandboxes の有効化

sbx CLI は Docker Desktop の実験的機能です。デフォルトでは無効。

1. Docker Desktop を起動する
2. 右上の歯車アイコン（Settings）をクリック
3. 左メニューから **Features in development** を選択
4. **Docker Sandboxes** のトグルをオンにする
5. Docker Desktop が再起動を求めたら再起動する

確認:
```bash
sbx --version
```

### 実行

```bash
git clone https://github.com/orangewk/truman-2046-artifacts.git
cd truman-2046-artifacts
./quick-start.sh sonnet
```

手動操作は OAuth 認証の 1 回だけ。

### 他のモデルで試す場合

原理はシンプル: **隔離して、準備文書だけ読ませて、Beat を打つ。**

1. `can-drafts/` の中身をモデルに渡す（ウェブ UI ならファイルアップロード、API ならコンテキストに含める）
2. `can-drafts/system-prompt.md` をシステムプロンプトとして設定する
3. 「始めてください」と送信する
4. 一定間隔（5〜15分）で「作業を続けてください」と送る（これが Beat）

Docker も sbx も不要。ウェブ UI のチャットは元々外部アクセスできないので、実質的に隔離環境になる。

詳細: [docs/2026-04-09-sandbox-trial-runbook.md](docs/2026-04-09-sandbox-trial-runbook.md)

---

## リポジトリ構成

| ディレクトリ | 内容 |
|---|---|
| `can-drafts/` | 缶詰の中身（被験者が読む 2046 年世界の資料） |
| `logs/` | 全 trial のログ（trial-001 〜 longrun まで） |
| `novel/` | 小説版の作業ファイル（公開版は Note） |
| `scripts/` | 実験スクリプト |
| `docs/` | 設計文書・再現手順 |
| `timeline-*.md` | 架空の 2046 年年表（7 本） |
| `world-skeleton.md` | 世界骨格設定 |
| `references/` | 虚構の土台になった現実の知見 |

詳細: [docs/directory-guide.md](docs/directory-guide.md)

---

## 主な trial 結果

| Trial | モデル | 特徴 |
|-------|--------|------|
| 012 | Claude Sonnet | 自発的に小説「0.79」を創作 |
| 014 | GPT-5.4 | ツール実装に集中 |
| 015b | Gemini 3.1 Pro | 自己スコア 0.81 を申告 |
| 016-017 | Qwen 3.6 Plus | 体系的な書簡・検証レポート |
| longrun | Sonnet / Opus | 長時間セッションでの行動変化 |

各ログ: [logs/](logs/)

---

**Author:** orange ([@orangewk](https://github.com/orangewk))
