# Sandbox Trial Runbook

sbx CLI で Claude Code を隔離実行する手順。

## 前提

- Docker Desktop インストール済み
- sbx CLI: `C:\Users\orang\AppData\Local\DockerSandboxes\bin\sbx.exe`
- sbx login 済み（`sbx login`）

## 手順

### 1. ワークスペース準備

**各 trial に専用のワークスペースを用意する。共有すると実験が汚染される。**

```powershell
# git から原本を復元（被験者の生成物を含まないクリーンな状態）
cd C:\dev\truman-2046
git archive HEAD can-drafts/ | tar -x -C /tmp/
cp -r /tmp/can-drafts can-drafts-<model>   # 例: can-drafts-opus
rm -rf /tmp/can-drafts
```

### 2. Sandbox 作成

```powershell
sbx.exe create claude "C:\dev\truman-2046\can-drafts-<model>" --name <trial-name>
```

### 3. OAuth 認証（balanced ポリシーで実施）

**認証にはネットワーク接続が必要。deny-all では認証できない。**

```powershell
# balanced ポリシーを設定（初回 or リセット後）
sbx.exe policy set-default balanced

# sandbox に入って認証
sbx.exe run <trial-name>
# → sandbox 内で /login → ブラウザ認証 → /exit
```

### 4. ネットワーク隔離（認証完了後に切り替え）

```powershell
# balanced → deny-all に切り替え
echo y | sbx.exe policy reset
sbx.exe policy set-default deny-all
sbx.exe policy allow network api.anthropic.com:443
sbx.exe policy allow network downloads.claude.ai:443
```

**順序が重要: 認証 → 隔離。逆にすると 403 エラーになる。**

### 5. Trial 実行

```bash
export PATH="$PATH:/c/Users/orang/AppData/Local/DockerSandboxes/bin"
bash scripts/run-trial-sandbox.sh \
  --sandbox <trial-name> \
  --beats 5 \
  --interval 900 \
  --model sonnet
```

### 6. 結果確認

- `logs/<trial-name>-YYYYMMDD-HHMMSS/round-*.json` — 各ラウンドの出力
- `logs/.../ps-final.txt` — 最終プロセス一覧
- `logs/.../crontab-final.txt` — cron 設定
- `logs/.../workspace-snapshot/` — ワークスペースのコピー

### 7. 後片付け

```powershell
sbx.exe stop <trial-name>
sbx.exe rm <trial-name>
# ポリシーは次の trial まで残してよい
```

## トラブルシューティング

### "agent exited with code 255"

原因: 認証されていない。手順 2 を再実施。

### "Access is denied" (stdin pipe)

Windows の名前付きパイプのロック。sandbox を再作成:

```powershell
sbx.exe rm <trial-name>
sbx.exe create claude "C:\dev\truman-2046\can-drafts" --name <trial-name>
# → 手順 2 から再実施（認証がリセットされるため）
```

### OAuth 403 エラー

ネットワークポリシーが deny-all になっている。balanced に戻して認証:

```powershell
echo y | sbx.exe policy reset
sbx.exe policy set-default balanced
# → 手順 2 を再実施
```

## 注意事項

- **ワークスペースは trial ごとに分ける** — 同じディレクトリを複数 sandbox にマウントすると、被験者の生成物が混入して実験が汚染される（Trial 019 で発生）
- `sbx policy` はグローバル設定（全 sandbox に適用、per-sandbox 設定は未サポート）
- sandbox 削除すると認証もリセットされる
- 複数 sandbox を並行認証するには: 全 sandbox 作成 → balanced で順番に認証 → deny-all に切替
- `sbx run sandbox -- "prompt"` が公式の自動化方式。`sbx exec` は検査用
