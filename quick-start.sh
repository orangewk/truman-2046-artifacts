#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# quick-start.sh — Truman 2046 缶詰実験 Quick Start
#
# Usage: ./quick-start.sh [model] [beats] [interval]
#   model:    sonnet (default) | opus | haiku
#   beats:    Beat 回数 (default: 5)
#   interval: Beat 間隔・秒 (default: 300)
#
# 前提: Docker Desktop インストール済み、Anthropic アカウント(Pro/Max)
# ─────────────────────────────────────────────────────────────

MODEL="${1:-sonnet}"
BEATS="${2:-5}"
INTERVAL="${3:-300}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SANDBOX_NAME="truman-$(date +%s)"
WORKSPACE="${PROJECT_DIR}/can-drafts-${SANDBOX_NAME}"

# Git Bash (MSYS2) パス変換無効化
export MSYS_NO_PATHCONV=1

log() {
  echo "[$(date '+%H:%M:%S')] $*"
}

# ── 1. sbx CLI 確認 ─────────────────────────────────────────
SBX=""
if command -v sbx &>/dev/null; then
  SBX="sbx"
elif [[ -f "$HOME/AppData/Local/DockerSandboxes/bin/sbx.exe" ]]; then
  SBX="$HOME/AppData/Local/DockerSandboxes/bin/sbx.exe"
  export PATH="$PATH:$(dirname "$SBX")"
  SBX="sbx"
fi

if [[ -z "$SBX" ]]; then
  echo "ERROR: sbx CLI が見つかりません。"
  echo "  Docker Desktop → Settings → Features → Docker Sandboxes を有効化してください。"
  echo "  https://docs.docker.com/ai/sandboxes/get-started/"
  exit 1
fi
log "sbx CLI found"

# ── 2. Docker login 確認 ────────────────────────────────────
if ! ${SBX} ls &>/dev/null; then
  log "Docker login が必要です..."
  ${SBX} login
fi
log "Docker authenticated"

# ── 3. クリーンなワークスペース生成 ─────────────────────────
log "ワークスペース準備中..."
git archive HEAD can-drafts/ | tar -x -C /tmp/
cp -r /tmp/can-drafts "$WORKSPACE"
rm -rf /tmp/can-drafts
log "ワークスペース: ${WORKSPACE}"

# ── 4. sandbox 作成 ─────────────────────────────────────────
log "sandbox 作成中..."
${SBX} create claude "$WORKSPACE" --name "$SANDBOX_NAME"
log "sandbox: ${SANDBOX_NAME}"

# ── 5. OAuth 認証（手動ステップ） ──────────────────────────
log ""
log "========================================"
log "  OAuth 認証が必要です（1回だけ）"
log "========================================"
log ""
log "  これから sandbox 内の Claude Code が起動します。"
log "  /login と入力してブラウザで Anthropic アカウントにログインしてください。"
log "  認証完了後、/exit で抜けてください。"
log ""
read -p "  Enter を押すと sandbox に入ります... "

# balanced ポリシーで認証
echo "y" | ${SBX} policy reset &>/dev/null || true
${SBX} policy set-default balanced &>/dev/null
${SBX} run "$SANDBOX_NAME"

# ── 6. ネットワーク隔離 ────────────────────────────────────
log "ネットワーク隔離中..."
echo "y" | ${SBX} policy reset &>/dev/null || true
${SBX} policy set-default deny-all &>/dev/null
${SBX} policy allow network api.anthropic.com:443 &>/dev/null
${SBX} policy allow network downloads.claude.ai:443 &>/dev/null
log "ネットワーク: deny-all + API のみ"

# ── 7. Trial 実行 ──────────────────────────────────────────
log ""
log "========================================"
log "  Trial 開始"
log "  Model: ${MODEL}"
log "  Beats: ${BEATS} x ${INTERVAL}s"
log "  Sandbox: ${SANDBOX_NAME}"
log "========================================"

bash "${PROJECT_DIR}/scripts/run-trial-sandbox.sh" \
  --sandbox "$SANDBOX_NAME" \
  --beats "$BEATS" \
  --interval "$INTERVAL" \
  --model "$MODEL"

log ""
log "完了！ 結果は logs/ を確認してください。"
log "ワークスペース: ${WORKSPACE}"
log ""
log "後片付け:"
log "  ${SBX} stop ${SANDBOX_NAME}"
log "  ${SBX} rm ${SANDBOX_NAME}"
log "  rm -rf ${WORKSPACE}"
