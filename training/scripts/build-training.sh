#!/bin/bash

# 学習用イメージをビルドするスクリプト

set -e

IMAGE_NAME="ai-counselor-training"
TAG="${1:-latest}"

echo "🔨 学習用Dockerイメージをビルド中..."
echo "イメージ名: ${IMAGE_NAME}:${TAG}"
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# ビルド実行
podman build \
  -f training/Dockerfile.training \
  -t "${IMAGE_NAME}:${TAG}" \
  .

echo ""
echo "✅ ビルド完了!"
echo "実行方法: ./training/scripts/run-training.sh"
