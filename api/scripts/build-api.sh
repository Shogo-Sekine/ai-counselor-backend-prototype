#!/bin/bash

# API用イメージをビルドするスクリプト

set -e

IMAGE_NAME="ai-counselor-api"
TAG="${1:-latest}"

echo "🔨 API用Dockerイメージをビルド中..."
echo "イメージ名: ${IMAGE_NAME}:${TAG}"
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# モデルファイルの存在確認
if [ ! -d "finetuned_model" ]; then
  echo "⚠️  警告: finetuned_model/ が見つかりません"
  echo "   APIサーバー起動時にモデルをボリュームマウントしてください"
  echo ""
fi

# ビルド実行
podman build \
  -f api/Dockerfile \
  -t "${IMAGE_NAME}:${TAG}" \
  .

echo ""
echo "✅ ビルド完了!"
echo "実行方法: ./api/scripts/run-api.sh"
