#!/bin/bash

# APIサーバーを起動するスクリプト

set -e

IMAGE_NAME="ai-counselor-api"
TAG="${1:-latest}"
CONTAINER_NAME="ai-counselor-api-server"
PORT="${2:-5000}"

echo "🚀 APIサーバーを起動します..."
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# モデルファイルの存在確認
if [ ! -d "finetuned_model" ]; then
  echo "❌ エラー: finetuned_model/ が見つかりません"
  echo "   先にモデルを学習してください: ./training/scripts/run-training.sh"
  exit 1
fi

# 既存のコンテナを停止・削除
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
  echo "🛑 既存のコンテナを停止・削除中..."
  podman stop "${CONTAINER_NAME}" 2>/dev/null || true
  podman rm "${CONTAINER_NAME}" 2>/dev/null || true
fi

echo "📡 ポート: ${PORT}"
echo "💾 モデル: $(pwd)/finetuned_model"
echo ""

# コンテナを起動
podman run -d \
  --name "${CONTAINER_NAME}" \
  -p "${PORT}:5000" \
  -v "$(pwd)/finetuned_model:/app/finetuned_model:ro" \
  --restart unless-stopped \
  "${IMAGE_NAME}:${TAG}"

echo ""
echo "✅ APIサーバーが起動しました!"
echo "URL: http://localhost:${PORT}"
echo ""
echo "動作確認:"
echo "  curl -X POST http://localhost:${PORT}/generate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"text\": \"こんにちは\"}' | jq"
echo ""
echo "ログ確認: podman logs -f ${CONTAINER_NAME}"
echo "停止: podman stop ${CONTAINER_NAME}"
