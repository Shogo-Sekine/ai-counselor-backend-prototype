# API環境用Dockerfile (軽量化版)
FROM python:3.11-slim-bookworm

# メタデータ
LABEL maintainer="AI Counselor Project"
LABEL description="Lightweight API server for fine-tuned model inference"

# pipの設定（タイムアウト対策）
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=5 \
    PIP_NO_CACHE_DIR=1

# 作業ディレクトリの設定
WORKDIR /app

# API用依存関係をコピーしてインストール
# レイヤーキャッシュを効率化するため、requirements.txtを先にコピー
COPY api/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY api/app.py ./

# 学習済みモデルをコピー (ビルド時に配置されている場合)
# 実行時にボリュームマウントする場合はこの行をコメントアウト
# COPY finetuned_model/ ./finetuned_model/

# 非rootユーザーを作成して使用 (セキュリティ向上)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# ポートを公開
EXPOSE 5000

# ヘルスチェック (オプション)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/generate', timeout=2)" || exit 1

# アプリケーションを起動
CMD ["python", "app.py"]
