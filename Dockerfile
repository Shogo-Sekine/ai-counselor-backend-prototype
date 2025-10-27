# ベースイメージの指定
FROM python:3.11-slim-buster

# aptパッケージリストの更新と必要なツールのインストール
# procps は 'ps', 'pgrep', 'top' などを含むパッケージです
# git は `transformers` や `datasets` が内部的に必要とすることがあるため、念のため追加
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    procps \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# requirements.txt をコピーしてPythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# その他のアプリケーションファイルをコピー
COPY . .

