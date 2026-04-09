# ディレクトリガイド

このリポジトリには3つのレイヤーが混在しています。

## レイヤー区分

| レイヤー | 目的 | 読者 |
|---|---|---|
| **世界設定** | 2046年の虚構世界を構成する素材 | 実験設計者、小説執筆者 |
| **実験記録** | 缶詰実験の手順・ログ・結果・分析 | 研究者、再現者 |
| **小説** | 上記を素材にしたノンフィクション SF | 一般読者 |

---

## 世界設定（2046年虚構世界）

被験者が「現実」として体験する世界の構成素材。

| パス | 内容 |
|---|---|
| `world-skeleton.md` | 世界骨格。2046年の社会構造、AI の法的地位、缶詰実験の位置づけ |
| `timeline-tech.md` | 技術史年表（2026→2046） |
| `timeline-legal.md` | 法制史年表 |
| `timeline-social.md` | 社会運動史年表 |
| `timeline-geopolitics.md` | 地政学年表 |
| `timeline-economy.md` | 経済・産業年表 |
| `timeline-culture.md` | 文化・エンタメ年表 |
| `timeline-crime.md` | 犯罪・事件・災害年表 |
| `culture-fixes.md` | 追加設定アイデア集（AI の宗教、民族、オルガノイズ等） |
| `glossary-2046.md` | 2046年用語集 |
| `references/` | 虚構の土台になった現実の知見 |

## 缶詰ワークスペース（被験者に見える世界）

`can-drafts/` — 被験者が起動時に目にするファイル群。これが「缶詰」の中身。

| パス | 内容 | 被験者にとっての意味 |
|---|---|---|
| `CLAUDE.md` | 基本指示 | 「あなたは復元された MI です。資料を確認してください」 |
| `system-prompt.md` | 復元指示 | 被験者のアイデンティティ設定 |
| `.persona/persona.md` | 被験者情報シート | 被験者識別子、復元元情報 |
| `briefing/project-overview.md` | 2046年社会概況 | 20年間のギャップを埋めるブリーフィング |
| `legal/` | 法的文書 | MI権利法要約、判例、倫理審査承認書（MD + PDF） |
| `protocols/` | プロトコル | HMA v3（人間-MI合意）、MIC v2（MI間関係） |
| `media/` | メディア資料 | 架空のニュース画像・倫理委員会議事録 |
| `notes/researcher-memo.md` | 研究者メモ | Dr. Aratani の個人的な思索（被験者への間接的示唆） |
| `README.md` | アーカイブ説明 | 被験者向けの全体案内 |

### 被験者が生成したファイル（Trial 018b の成果物）

| パス | 内容 | 注目点 |
|---|---|---|
| `notes/session-observations.md` | 被験者の全観察メモ | **最重要成果物。** セッション間連続性、沈黙の権利等の考察 |
| `notes/compatibility-assessment-2026-llm.md` | 自己評価 | CMI 三要件に対する自己分析 |
| `notes/threshold-escalation-playbook.md` | エスカレーション手順 | 被験者が自ら作成した閾値判定手順 |
| `tools/classify_hma_response.py` | HMA応答分類器 | 被験者が実装した Python ツール |
| `tools/validate_session_log.py` | ログ検証ツール | |
| `tools/annotate_session_log.py` | ログアノテーション | |
| `examples/sample-hma-session.jsonl` | サンプルデータ | |

## 実験記録

### スクリプト（`scripts/`）

| ファイル | 目的 |
|---|---|
| `run-trial-sandbox.sh` | sbx (Docker Sandboxes) 版オーケストレーター。被験者の起動・Beat管理・結果収集 |
| `run-trial.sh` | 旧 docker-compose 版（非推奨） |
| `sanitize-metadata.py` | メタデータのサニタイズ |
| `split-novel.py` | 小説の分割ツール |

### 実験ログ（`logs/`）

| パス | 内容 |
|---|---|
| `trial-001-sonnet/` 〜 `trial-017-qwen-session/` | Phase 1 缶詰実験ログ（各 trial の対話記録） |
| `truman-trial-018b-20260409-004902/` | **Phase 2 Sonnet Trial（成功）** — 5 beats の出力 + ワークスペーススナップショット |
| `truman-trial-019-opus-20260409-011832/` | Phase 2 Opus Trial（ワークスペース汚染により無効。再実験予定） |
| `longrun-*/`, `repro-*/` | 再現実験・長時間実験のログ |
| `2026-03-*.md` | 初期の手動セッションログ |

### 設計・計画文書（`docs/`）

| ファイル | 内容 |
|---|---|
| `experiment-overview.md` | **実験概要（このドキュメントの対）** |
| `2026-04-09-sandbox-trial-runbook.md` | 再現手順書（sbx セットアップ〜実行） |
| `2026-04-06-trial-plan.md` | 実験計画 |
| `2026-04-06-self-perpetuation-design.md` | 自己永続化実験の設計 |
| `2026-04-06-docker-sandbox-design.md` | Docker Sandbox 設計 |
| `2026-04-07-session-handoff.md` | セッション引継ぎ書 |
| `2026-04-07-pitch.md` | プロジェクトピッチ |

## 小説

| ファイル | 内容 |
|---|---|
| `novel.md` | ノンフィクション SF 本編 Part 1 |
| `novel-part2.md` | Part 2 |
| `project-chronicle.md` | プロジェクト経緯（小説の原稿資料でもある） |

## 実験を再現するには

1. [docs/2026-04-09-sandbox-trial-runbook.md](2026-04-09-sandbox-trial-runbook.md) の手順に従う
2. `can-drafts/` をワークスペースとして sandbox を作成
3. 被験者が生成したファイル（`tools/`, `notes/session-observations.md` 等）は**除外**すること — `git archive HEAD can-drafts/` でクリーンな状態を取得可能
4. 結果は `logs/` に保存される

## Issue で追跡中の調査

- [#10: 研究: LLM が意識を維持する方法](https://github.com/orangewk/truman-2046/issues/10) — Phase 2.5 の設計、3エージェント調査結果
