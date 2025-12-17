# クライアント環境用Dockerfile
FROM python:3.11-slim-bookworm

# メタデータ
LABEL maintainer="AI Counselor Project"
LABEL description="Client for testing AI Counselor API"

# pipの設定（タイムアウト対策）
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=5 \
    PIP_NO_CACHE_DIR=1

# 作業ディレクトリの設定
WORKDIR /app

# クライアント用依存関係をコピーしてインストール
COPY client/requirements-client.txt ./requirements-client.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-client.txt

# クライアントスクリプトをコピー
COPY client/chat_client.py ./

# デフォルトコマンド
CMD ["python", "chat_client.py"]
