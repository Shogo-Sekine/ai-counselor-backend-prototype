#!/bin/bash

# モデル学習を実行するスクリプト

set -e

IMAGE_NAME="ai-counselor-training"
TAG="${1:-latest}"

echo "🚀 モデル学習を開始します..."
echo ""

# プロジェクトルートで実行
cd "$(dirname "$0")/../.."

# データディレクトリとモデル保存先の存在確認
if [ ! -d "data" ]; then
  echo "❌ エラー: data/ ディレクトリが見つかりません"
  exit 1
fi

# モデル保存先ディレクトリを作成
mkdir -p finetuned_model

echo "📊 学習データ: $(pwd)/data"
echo "💾 モデル保存先: $(pwd)/finetuned_model"
echo ""

# コンテナで学習実行
podman run -it --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/finetuned_model:/app/finetuned_model" \
  "${IMAGE_NAME}:${TAG}"

echo ""
echo "✅ 学習完了!"
echo "学習済みモデルは finetuned_model/ に保存されました"
