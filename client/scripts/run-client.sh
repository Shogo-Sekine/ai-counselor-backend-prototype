#!/bin/bash

# チャットクライアントを起動するスクリプト

set -e

IMAGE_NAME="ai-counselor-client"
TAG="${1:-latest}"
API_URL="${2:-http://host.containers.internal:5000}"

echo "🚀 チャットクライアントを起動します..."
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# APIサーバーの疎通確認
echo "📡 APIサーバー接続先: ${API_URL}"
echo ""
echo "ℹ️  注意: APIサーバーが起動していることを確認してください"
echo "   podman ps | grep ai-counselor-api-server"
echo ""

# コンテナでクライアント実行
# host.containers.internal でホストマシンにアクセス (Podman/Docker Desktop)
podman run -it --rm \
  -e API_URL="${API_URL}/generate" \
  "${IMAGE_NAME}:${TAG}"

echo ""
echo "✅ クライアント終了"
