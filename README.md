# AI Counselor Backend Prototype

AIカウンセラーのバックエンドプロトタイプです。日本語GPT-2モデルをファインチューニングし、Flask APIとして提供します。

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [アーキテクチャ](#アーキテクチャ)
- [前提条件](#前提条件)
- [クイックスタート](#クイックスタート)
  - [1. モデル学習環境](#1-モデル学習環境)
  - [2. APIサーバー環境](#2-apiサーバー環境)
  - [3. クライアント環境](#3-クライアント環境)
- [詳細ガイド](#詳細ガイド)
- [トラブルシューティング](#トラブルシューティング)

---

## プロジェクト概要

このプロジェクトは3つの環境に分離されています:

1. **Training環境**: モデルのファインチューニング
2. **API環境**: 学習済みモデルを使った推論APIサーバー
3. **Client環境**: APIテスト用クライアント

すべての環境がコンテナ化されており、ローカルマシンにPython環境を構築する必要はありません。

詳細な環境分離の設計思想は [`environment-separation-plan.md`](./environment-separation-plan.md) を参照してください。

---

## アーキテクチャ

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Training       │      │  API Server     │      │  Client         │
│  Environment    │──┐   │  Environment    │◄─────│  Environment    │
│                 │  │   │                 │      │                 │
│  - finetune.py  │  │   │  - Flask API    │      │  - chat CLI     │
│  - dataset      │  │   │  - Model        │      │  - HTTP client  │
└─────────────────┘  │   └─────────────────┘      └─────────────────┘
                     │
                     ▼
             finetuned_model/
             (学習済みモデル)
```

---

## 前提条件

### 必須
- **macOS** (その他のOSでも動作しますが、手順はmacOS向けです)
- **Podman** または **Docker** (コンテナランタイム)
  ```bash
  # Podmanのインストール (推奨)
  brew install podman
  podman machine init
  podman machine start
  
  # またはDockerのインストール
  brew install --cask docker
  ```

### オプション (API動作確認用)
- **jq** - JSONレスポンスを整形表示
  ```bash
  brew install jq
  ```

---

## クイックスタート

### 1. モデル学習環境

学習データからモデルをファインチューニングします。

#### 1.1 学習用Dockerイメージをビルド

```bash
# スクリプトでビルド (推奨)
./training/scripts/build-training.sh

# または手動でビルド
podman build -f training/Dockerfile.training -t ai-counselor-training .
```

#### 1.2 学習を実行

```bash
# スクリプトで実行 (推奨)
./training/scripts/run-training.sh

# または手動で実行
podman run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/finetuned_model:/app/finetuned_model \
  ai-counselor-training
```

**実行時のポイント:**
- `-v $(pwd)/data:/app/data` - 学習データをマウント
- `-v $(pwd)/finetuned_model:/app/finetuned_model` - 学習済みモデルの保存先
- `--rm` - 実行後にコンテナを自動削除

#### 1.3 学習の進捗確認

学習中は以下のようなログが表示されます:

```
Loading checkpoint shards: 100%|██████████| 1/1 [00:00<00:00,  2.34it/s]
Starting model fine-tuning...
{'loss': 2.345, 'learning_rate': 5e-05, 'epoch': 1.0}
{'loss': 1.890, 'learning_rate': 4e-05, 'epoch': 2.0}
...
Fine-tuning completed. Model saved to: ./finetuned_model
```

学習完了後、`finetuned_model/` ディレクトリに以下のファイルが生成されます:
- `config.json`
- `model.safetensors`
- `tokenizer.json`
- その他のモデルファイル

---

### 2. APIサーバー環境

学習済みモデルを使ってAPIサーバーを起動します。

#### 2.1 APIイメージをビルド

```bash
# スクリプトでビルド (推奨)
./api/scripts/build-api.sh

# または手動でビルド
podman build -f api/Dockerfile -t ai-counselor-api .
```

#### 2.2 APIサーバーを起動

```bash
# スクリプトで起動 (推奨)
./api/scripts/run-api.sh

# または手動で起動
podman run -d \
  --name ai-counselor-api-server \
  -p 5000:5000 \
  -v $(pwd)/finetuned_model:/app/finetuned_model:ro \
  ai-counselor-api
```

#### 2.3 起動確認

コンテナが起動しているか確認:

```bash
podman ps
```

ログを確認:

```bash
podman logs -f ai-counselor-api-server
```

正常に起動すると以下のようなログが表示されます:

```
Loading fine-tuned model from ./finetuned_model...
AI model loaded successfully!
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

#### 2.4 APIの動作確認

別のターミナルで以下のコマンドを実行:

```bash
# シンプルなテスト
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは"}'

# jqで整形表示
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "最近疲れています"}' | jq
```

**期待されるレスポンス:**
```json
{
  "response": "お疲れのようですね。少し休息が必要かもしれません。"
}
```

---

### 3. クライアント環境

対話型チャットクライアントでAPIをテストします。

#### 3.1 クライアントイメージをビルド

```bash
# スクリプトでビルド (推奨)
./client/scripts/build-client.sh

# または手動でビルド
podman build -f client/Dockerfile -t ai-counselor-client .
```

#### 3.2 チャットクライアントを起動

```bash
# スクリプトで起動 (推奨)
./client/scripts/run-client.sh

# または手動で起動
podman run -it --rm \
  -e API_URL="http://host.containers.internal:5000/generate" \
  ai-counselor-client
```

> **Note**: コンテナ内からホストのAPIサーバーにアクセスするため、`host.containers.internal` を使用します。

#### 3.3 対話例

```
AIカウンセラープロトタイプへようこそ！ (終了するには 'exit' または 'quit' と入力)
API接続先: http://host.containers.internal:5000/generate

あなた: こんにちは
AI: 考え中...
AI: こんにちは、何かお困りですか?

あなた: 最近仕事で悩んでいます
AI: 考え中...
AI: 仕事の悩みは辛いですね。どのようなことでお悩みですか?

あなた: exit
AI: さようなら！
```

#### 3.4 ローカル環境で実行する場合 (オプション)

ローカルのPython環境で実行したい場合:

```bash
cd client
python -m venv venv
source venv/bin/activate
pip install -r requirements-client.txt
API_URL=http://localhost:5000/generate python chat_client.py
```

---

## 詳細ガイド

### 環境変数の設定

APIサーバーのURLやポートをカスタマイズする場合:

```bash
# .envファイルを作成
cat > .env << EOF
API_HOST=0.0.0.0
API_PORT=5000
MODEL_PATH=./finetuned_model
EOF
```

### GPU環境での学習 (オプション)

GPU環境でDockerを使用する場合:

```bash
# GPU対応で学習を実行
docker run -it --rm --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/finetuned_model:/app/finetuned_model \
  ai-counselor-training \
  python finetune_model.py
```

### 学習データのカスタマイズ

`data/fine_tune_data.jsonl` を編集して独自のデータで学習:

```jsonl
{"text": "ユーザー: こんにちは\nAI: こんにちは、お元気ですか?"}
{"text": "ユーザー: 疲れました\nAI: お疲れ様です。少し休憩しましょう。"}
```

---

## トラブルシューティング

### コンテナが起動しない

```bash
# Podmanマシンの状態確認
podman machine list

# 起動していない場合
podman machine start

# コンテナのログを確認
podman logs ai-counselor-api-server
```

### APIサーバーが応答しない

```bash
# ポートが使用中か確認
lsof -i :5000

# 別のポートで起動
docker run -p 8080:5000 ...
```

### モデルファイルが見つからない

```bash
# モデルファイルの存在確認
ls -la finetuned_model/

# 学習が完了しているか確認
# model.safetensors または pytorch_model.bin があればOK
```

### メモリ不足エラー

学習時にメモリ不足になる場合:

1. `finetune_model.py` のバッチサイズを小さくする:
   ```python
   per_device_train_batch_size=1  # デフォルトは1
   ```

2. エポック数を減らす:
   ```python
   num_train_epochs=50  # デフォルトは100
   ```

---

## プロジェクト構造

```
ai-counselor-backend-prototype/
├── README.md                          # このファイル
├── QUICKSTART.md                      # クイックスタートガイド
├── environment-separation-plan.md     # 環境分離の設計ドキュメント
├── .gitignore
├── .dockerignore
│
├── training/                          # 学習環境
│   ├── Dockerfile.training           # 学習用Dockerfile
│   ├── requirements-training.txt     # 学習用依存関係
│   ├── finetune_model.py            # モデル学習スクリプト
│   └── scripts/
│       ├── build-training.sh        # イメージビルド
│       └── run-training.sh          # 学習実行
│
├── api/                               # APIサーバー環境
│   ├── Dockerfile                    # API用Dockerfile (軽量化)
│   ├── requirements.txt              # API用依存関係
│   ├── app.py                        # Flask APIサーバー
│   └── scripts/
│       ├── build-api.sh             # イメージビルド
│       ├── run-api.sh               # サーバー起動
│       └── stop-api.sh              # サーバー停止
│
├── client/                            # クライアント環境
│   ├── Dockerfile                    # クライアント用Dockerfile
│   ├── chat_client.py                # テスト用クライアント
│   ├── requirements-client.txt       # クライアント用依存関係
│   ├── README.md
│   └── scripts/
│       ├── build-client.sh          # イメージビルド
│       └── run-client.sh            # クライアント起動
│
├── data/                              # 学習データ
│   └── fine_tune_data.jsonl
│
└── finetuned_model/                   # 学習済みモデル (git管理外)
    ├── config.json
    ├── model.safetensors
    └── ...
```

---

## 次のステップ

- [x] 環境の完全分離 (`training/`, `api/`, `client/` への再編成)
- [ ] Docker Composeでの統合管理
- [ ] CI/CDパイプラインの構築
- [ ] 本番環境へのデプロイ

詳細は [`environment-separation-plan.md`](./environment-separation-plan.md) を参照してください。

---

## ライセンス

このプロジェクトはプロトタイプです。

## 参考リンク

- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [rinna/japanese-gpt2-small](https://huggingface.co/rinna/japanese-gpt2-small)
- [Flask Documentation](https://flask.palletsprojects.com/)
