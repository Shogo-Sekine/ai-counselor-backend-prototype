# AI Counselor Client

APIサーバーと対話するためのシンプルなクライアントです。

## セットアップ方法

### オプション1: コンテナで実行 (推奨)

ローカル環境を汚さずにクライアントを実行できます。

```bash
# イメージをビルド
./scripts/build-client.sh

# クライアントを起動
./scripts/run-client.sh
```

**カスタムAPI URLを指定する場合:**

```bash
# 第2引数でAPI URLを指定
./scripts/run-client.sh latest http://custom-host:8080
```

### オプション2: ローカル実行

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements-client.txt

# クライアントを起動
python chat_client.py
```

## 使い方

### 対話型チャット

APIサーバーが起動していることを確認してください:

```bash
# APIサーバーの起動確認
podman ps | grep ai-counselor-api-server

# 起動していない場合
cd ..
./api/scripts/run-api.sh
```

### カスタムAPIエンドポイント

環境変数でAPIのURLを変更できます:

```bash
# ローカル実行の場合
API_URL=http://localhost:8080/generate python chat_client.py

# コンテナ実行の場合はスクリプトの第2引数で指定
./scripts/run-client.sh latest http://localhost:8080
```

## トラブルシューティング

### API接続エラー (コンテナ実行時)

```
API接続エラー: HTTPConnectionPool(host='localhost', port=5000)
```

**原因:** コンテナ内から`localhost`でホストのAPIサーバーにアクセスできない

**解決策:** `host.containers.internal`を使用（デフォルト設定済み）

```bash
# スクリプトがデフォルトで設定
./scripts/run-client.sh
```

### API接続エラー (ローカル実行時)

```
API接続エラー: HTTPConnectionPool(host='localhost', port=5000)
```

**解決策:** APIサーバーが起動しているか確認:

```bash
curl http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```
