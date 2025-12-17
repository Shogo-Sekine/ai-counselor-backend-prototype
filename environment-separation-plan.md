# 環境分離改善プラン

## 現状分析

### 現在の課題
- モデル学習環境、APIサーバー環境、クライアント環境が混在
- 単一の`Dockerfile`と`requirements.txt`ですべてを管理
- 本番環境に不要な学習用ライブラリが含まれる
- リソースの無駄とセキュリティリスク

### 影響
- Dockerイメージサイズの肥大化
- デプロイ時間の増加
- 本番環境での脆弱性リスク増大
- 開発・本番環境の境界が曖昧

---

## 改善プラン: 3環境分離アーキテクチャ

### 1. モデル学習環境 (Training Environment)

#### 目的
- ファインチューニングの実行
- 学習データの管理
- 学習済みモデルの生成

#### 構成
```
training/
├── Dockerfile.training        # 学習専用Dockerfile
├── requirements-training.txt  # 学習用依存関係
├── finetune_model.py         # 既存ファイルを移動
├── data/
│   └── fine_tune_data.jsonl
└── scripts/
    ├── build-training.sh     # イメージビルドスクリプト
    └── run-training.sh       # 学習実行スクリプト
```

#### 依存関係 (requirements-training.txt)
```
transformers==4.42.1
datasets==3.6.0
torch==2.3.1
accelerate==1.8.1
sentencepiece==0.2.0
```

#### 実行方法
**オプション1: コンテナ実行 (推奨)**
```bash
# イメージをビルド
podman build -f training/Dockerfile.training -t ai-counselor-training .

# コンテナで学習実行 (CPU)
podman run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/finetuned_model:/app/finetuned_model \
  ai-counselor-training

# GPU環境の場合 (docker使用)
docker run -it --rm --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/finetuned_model:/app/finetuned_model \
  ai-counselor-training
```

**オプション2: ローカル実行 (非推奨)**
```bash
# ローカル環境を汚したくない場合はコンテナ実行を推奨
python -m venv venv-training
source venv-training/bin/activate
pip install -r training/requirements-training.txt
python training/finetune_model.py
```

#### 成果物
- `finetuned_model/` ディレクトリ (モデルファイル一式)
- このディレクトリをAPIサーバーにデプロイ

---

### 2. APIサーバー環境 (Production Environment)

#### 目的
- 学習済みモデルを使った推論API提供
- 本番環境での安定稼働
- 高速レスポンス

#### 構成
```
api/
├── Dockerfile                 # 本番用Dockerfile (軽量化)
├── requirements.txt           # API用依存関係のみ
├── app.py                     # 既存ファイルを移動
├── finetuned_model/          # 学習済みモデル (デプロイ時)
└── scripts/
    ├── build-api.sh
    ├── run-api.sh
    └── deploy.sh
```

#### 依存関係 (api/requirements.txt)
```
Flask==3.0.3
transformers==4.42.1
torch==2.3.1
sentencepiece==0.2.0
```

#### Dockerfile最適化ポイント
```dockerfile
# マルチステージビルドで軽量化
FROM python:3.11-slim-bookworm AS base

# 実行時に不要なビルドツールを削除
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のみ先にインストール (キャッシュ効率化)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードとモデルをコピー
COPY app.py .
COPY finetuned_model/ ./finetuned_model/

# 非rootユーザーで実行 (セキュリティ向上)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
```

#### デプロイフロー
```bash
# 1. モデルを学習環境から取得
scp -r training-server:~/finetuned_model ./api/

# 2. APIイメージをビルド
cd api
docker build -t ai-counselor-api:v1.0 .

# 3. コンテナ起動
docker run -d \
  --name ai-counselor-api \
  -p 5000:5000 \
  --restart unless-stopped \
  ai-counselor-api:v1.0
```

#### 本番環境推奨構成
- **オーケストレーション**: Kubernetes または Docker Compose
- **ロードバランサー**: nginx / ALB
- **監視**: Prometheus + Grafana
- **ログ**: fluentd / CloudWatch

---

### 3. クライアント環境 (Client/Development Environment)

#### 目的
- API動作確認
- 開発時のテスト
- デモンストレーション

#### 構成
```
client/
├── chat_client.py            # 既存ファイルを移動
├── requirements-client.txt   # クライアント用依存関係
└── README.md                 # 使い方
```

#### 依存関係 (client/requirements-client.txt)
```
requests==2.32.4
```

#### 実行方法
```bash
# ローカルで実行 (コンテナ化不要)
cd client
python -m venv venv
source venv/bin/activate
pip install -r requirements-client.txt

# APIサーバーに接続
python chat_client.py
```

---

## ディレクトリ構造 (改善後)

```
ai-counselor-backend-prototype/
├── README.md                          # プロジェクト全体の説明
├── environment-separation-plan.md     # このドキュメント
│
├── training/                          # 学習環境
│   ├── Dockerfile.training
│   ├── requirements-training.txt
│   ├── finetune_model.py
│   ├── data/
│   │   └── fine_tune_data.jsonl
│   └── scripts/
│       └── train.sh
│
├── api/                               # APIサーバー環境
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── finetuned_model/              # デプロイ時に配置
│   └── scripts/
│       ├── build-api.sh
│       ├── run-api.sh
│       └── deploy.sh
│
├── client/                            # クライアント環境
│   ├── chat_client.py
│   ├── requirements-client.txt
│   └── README.md
│
└── docs/                              # ドキュメント
    ├── api-integration-plan.md
    └── deployment-guide.md
```

---

## 実装ステップ

### Phase 1: ディレクトリ構造の再編成
- [ ] `training/`, `api/`, `client/` ディレクトリ作成
- [ ] 既存ファイルを適切なディレクトリに移動
- [ ] requirements.txt を3つに分割

### Phase 2: Docker構成の最適化
- [ ] `api/Dockerfile` の軽量化 (マルチステージビルド)
- [ ] `training/Dockerfile.training` の作成
- [ ] `.dockerignore` の作成

### Phase 3: スクリプトの整備
- [ ] 学習用スクリプト (`training/scripts/build-training.sh`, `run-training.sh`)
- [ ] APIビルド・デプロイスクリプト (`api/scripts/`)
- [ ] docker-compose.yml の作成 (開発環境用)

### Phase 4: ドキュメント整備
- [ ] README.md の更新
- [ ] 各環境のREADME作成
- [ ] デプロイガイドの作成

### Phase 5: CI/CDパイプライン (将来)
- [ ] GitHub Actions でモデル学習自動化
- [ ] APIイメージの自動ビルド・プッシュ
- [ ] 自動デプロイ設定

---

## 期待される効果

### セキュリティ向上
- 本番環境に学習コードが含まれない
- 最小限の依存関係でアタックサーフェス削減
- 非rootユーザーでの実行

### パフォーマンス向上
- Dockerイメージサイズ: 推定 50% 削減
- デプロイ時間: 推定 40% 短縮
- 起動時間: メモリ使用量削減により高速化

### 運用効率向上
- 環境ごとの責任範囲が明確
- トラブルシューティングが容易
- スケーリング戦略が立てやすい

### 開発効率向上
- 学習とAPI開発を並行作業可能
- 依存関係の更新影響範囲が限定的
- テスト環境の構築が容易
- **ローカル環境を汚さずにクリーンな開発環境を維持**

---

## 移行時の注意点

### 既存の動作保証
- 既存の `Dockerfile` と `requirements.txt` は当面維持
- 新環境への移行を段階的に実施
- ロールバック手順を明確化

### データの扱い
- `finetuned_model/` は git に含めない (.gitignore に追加)
- モデルファイルは別途管理 (S3, GCS, 社内ストレージ)
- 学習データも機密性に応じて管理

### 環境変数管理
- API URL、ポート番号などは環境変数化
- `.env` ファイルでローカル設定管理
- 本番環境はシークレット管理ツール使用

### コンテナ実行時の注意
- ボリュームマウントのパス権限に注意 (特にLinux)
- `--rm` フラグでコンテナを自動削除し、ディスク容量を節約
- 学習中のログは標準出力に出力し、必要に応じてリダイレクト

---

## 代替案: Docker Compose による統合管理

3環境を完全分離せず、Docker Compose で管理する軽量版アプローチ:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 学習サービス (手動実行)
  training:
    build:
      context: .
      dockerfile: training/Dockerfile.training
    volumes:
      - ./data:/app/data
      - ./finetuned_model:/app/finetuned_model
    profiles: ["training"]  # 明示的に指定時のみ起動

  # APIサーバー
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    volumes:
      - ./finetuned_model:/app/finetuned_model:ro
    restart: unless-stopped

  # nginxリバースプロキシ (オプション)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
```

実行例:
```bash
# 学習実行
docker-compose --profile training up training

# APIサーバー起動
docker-compose up -d api

# クライアントはローカルで実行
python client/chat_client.py
```

---

## 推奨事項

**推奨アプローチ: フル分離 (本プラン)**
- 本番環境での運用を見据える場合
- セキュリティ要件が高い場合
- 複数環境での展開を想定する場合

**代替アプローチ: Docker Compose**
- 小規模プロトタイプの場合
- 開発環境での迅速な検証が目的の場合
- リソースが限られている場合

現状のプロジェクトフェーズと今後の展開を考慮し、**フル分離アプローチ**を推奨します。
