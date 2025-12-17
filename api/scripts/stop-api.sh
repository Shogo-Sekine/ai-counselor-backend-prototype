#!/bin/bash

# APIサーバーを停止するスクリプト

set -e

CONTAINER_NAME="ai-counselor-api-server"

echo "🛑 APIサーバーを停止します..."

if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
  podman stop "${CONTAINER_NAME}"
  echo "✅ APIサーバーを停止しました"
else
  echo "⚠️  APIサーバーは起動していません"
fi
