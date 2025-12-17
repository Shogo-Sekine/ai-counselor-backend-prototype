# クイックスタートガイド

このガイドでは、リポジトリをcloneしてから動作確認するまでの最短手順を説明します。

## 前提条件

- Podman または Docker がインストール済み
- macOS, Linux, または Windows (WSL2)

## 手順

### 1️⃣ リポジトリをクローン

```bash
git clone https://github.com/Shogo-Sekine/ai-counselor-backend-prototype.git
cd ai-counselor-backend-prototype
```

### 2️⃣ モデルを学習

```bash
# イメージをビルド
./training/scripts/build-training.sh

# 学習を実行 (数分〜数十分かかります)
./training/scripts/run-training.sh
```

学習が完了すると `finetuned_model/` ディレクトリにモデルが保存されます。

### 3️⃣ APIサーバーを起動

```bash
# イメージをビルド
./api/scripts/build-api.sh

# サーバーを起動
./api/scripts/run-api.sh
```

### 4️⃣ 動作確認

**curlでテスト:**

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは"}' | jq
```

**クライアントでテスト (推奨):**

```bash
# イメージをビルド
./client/scripts/build-client.sh

# クライアントを起動
./client/scripts/run-client.sh
```

**ローカル環境でテスト (オプション):**

```bash
cd client
python -m venv venv
source venv/bin/activate
pip install -r requirements-client.txt
API_URL=http://localhost:5000/generate python chat_client.py
```

## よくある質問

### Q: 学習にどのくらい時間がかかりますか?

A: CPUで10〜30分程度です。GPU環境では数分で完了します。

### Q: ポート5000が使用中です

A: 別のポートで起動してください:

```bash
podman run -d \
  --name ai-counselor-api-server \
  -p 8080:5000 \
  -v $(pwd)/finetuned_model:/app/finetuned_model:ro \
  ai-counselor-api
```

### Q: モデルファイルが大きすぎてGitにpushできません

A: `.gitignore` でモデルは除外されています。別途ファイル共有サービスで共有してください。

## トラブルシューティング

問題が発生した場合は [README.md](./README.md#トラブルシューティング) のトラブルシューティングセクションを参照してください。
