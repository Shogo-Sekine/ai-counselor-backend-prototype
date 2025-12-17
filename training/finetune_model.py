import os
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import torch

# 既存のモデルとトークナイザーをロード
# rinna/japanese-gpt2-small は比較的小さなモデルで、CPU学習にも向いています
# MODEL_NAME = "rinna/japanese-gpt2-small"
MODEL_NAME = "rinna/japanese-gpt2-medium"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# トークナイザーのパディングトークンを設定 (必要であれば)
# GPT-2系列のモデルでは、pad_tokenがeos_token（End-Of-Sentenceトークン）と同じであると都合が良いことが多いです
if tokenizer.pad_token is None:
  tokenizer.pad_token = tokenizer.eos_token

# データセットのロード
# data_filesで指定するパスは、Dockerコンテナ内でのパスです。
# ホストの ./data/fine_tune_data.jsonl がコンテナの /app/data/fine_tune_data.jsonl にマウントされます。
data_files = {"train": "data/fine_tune_data.jsonl"}
dataset = load_dataset("json", data_files=data_files)

# データセットをトークン化する関数
def tokenize_function(examples):
  # 各テキストをトークン化し、モデルの最大長に合わせて切り詰めます
  # return_attention_mask=False は、attention_mask が不要な場合（今回のシンプルなCausalLMでは通常不要）に指定
  return tokenizer(examples["text"], truncation=True, max_length=128, return_attention_mask=False)

# データセットをトークン化
tokenized_datasets = dataset.map(
  tokenize_function,
  batched=True,
  remove_columns=["text"] # 元のテキストカラムは、トークン化後は不要なので削除
)

# Causal Language Modeling (CLM) のためのデータコレーター
# CLMでは、モデルの入力とラベル（正解）が同じになるようにデータを準備します。
# これにより、モデルは「次のトークンを予測する」タスクを学習します。
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False) # mlm=False でCausalLM用

# 学習設定 (TrainingArguments)
# CPU学習を考慮し、エポック数やバッチサイズを調整します。
output_dir = "./finetuned_model" # 学習済みモデルの保存先ディレクトリ
training_args = TrainingArguments(
  output_dir=output_dir,
  overwrite_output_dir=True,
  num_train_epochs=30,           # エポック数（学習の繰り返し回数）- お試しなので少なめに
  per_device_train_batch_size=1, # バッチサイズ - CPUでメモリ消費を抑えるため1に設定
  save_steps=1000,              # モデルを保存するステップ数（今回はデータが少ないので到達しない可能性が高い）
  save_total_limit=1,           # 保存するチェックポイントの最大数
  logging_dir='./logs',         # ログディレクトリ
  logging_steps=10,             # ログを出力するステップ数
  evaluation_strategy="no",     # 評価を行わない（まずはシンプルに学習だけ）
  seed=42,                      # 再現性のためのシード値
  # CPUで学習するため、fp16=True は指定しません
)

# トレーナーの初期化と学習の開始
trainer = Trainer(
  model=model,
  args=training_args,
  train_dataset=tokenized_datasets["train"],
  tokenizer=tokenizer,
  data_collator=data_collator,
)

print("Starting model fine-tuning...")
trainer.train()
print("Fine-tuning completed. Model saved to:", output_dir)

# 学習済みモデルとトークナイザーを明示的に保存 (Trainerが自動で保存しますが、確実にするため)
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print("Model and tokenizer explicitly saved to:", output_dir)
