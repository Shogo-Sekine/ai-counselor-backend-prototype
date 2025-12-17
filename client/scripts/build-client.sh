#!/bin/bash

# クライアント用イメージをビルドするスクリプト

set -e

IMAGE_NAME="ai-counselor-client"
TAG="${1:-latest}"

echo "🔨 クライアント用Dockerイメージをビルド中..."
echo "イメージ名: ${IMAGE_NAME}:${TAG}"
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# ビルド実行
podman build \
  -f client/Dockerfile \
  -t "${IMAGE_NAME}:${TAG}" \
  .

echo ""
echo "✅ ビルド完了!"
echo "実行方法: ./client/scripts/run-client.sh"
