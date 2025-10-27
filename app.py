from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline # pipelineだけでなく個別にインポート
import sys
import os # osモジュールをインポート

app = Flask(__name__)

# モデルのパスを定義
# finetuned_model ディレクトリがアプリのルートディレクトリにあることを想定
FINETUNED_MODEL_PATH = "./finetuned_model"

try:
  # 学習済みモデルが存在するか確認し、あればそちらをロード
  # 修正: pytorch_model.bin または model.safetensors のどちらかがあればOKとする
  if os.path.exists(FINETUNED_MODEL_PATH) and \
    (os.path.exists(os.path.join(FINETUNED_MODEL_PATH, "pytorch_model.bin")) or \
    os.path.exists(os.path.join(FINETUNED_MODEL_PATH, "model.safetensors"))) and \
    os.path.exists(os.path.join(FINETUNED_MODEL_PATH, "config.json")):
    print(f"Loading fine-tuned model from {FINETUNED_MODEL_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(FINETUNED_MODEL_PATH)
  else:
    print(f"Fine-tuned model not found at {FINETUNED_MODEL_PATH}. Loading base model 'rinna/japanese-gpt2-small'...")
    tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-small")
    model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-small")

  # トークナイザーのパディングトークンを設定
  if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

  # pipeline を再構築
  generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1) # device=-1 はCPU
  print("AI model loaded successfully!")

except Exception as e:
  print(f"Error loading AI model: {e}")
  sys.exit(1)

# --- ここから下の部分は変更なし ---

@app.route('/generate', methods=['POST'])
def generate_text():
  data = request.get_json()
  if not data or 'text' not in data:
    return jsonify({'error': 'Missing "text" in request body'}), 400

  input_text = data['text']
  print(f"Received input: '{input_text}'")

  try:
    generated_response = generator(
      input_text,
      max_new_tokens=50,
      do_sample=True,
      temperature=0.7,
      top_k=50,
      top_p=0.95,
      num_return_sequences=1,
    )

    response_text = generated_response[0]['generated_text']

    if response_text.startswith(input_text):
      response_text = response_text[len(input_text):].strip()

    if not response_text:
      response_text = "すみません、よくわかりません。"

    print(f"Generated response: '{response_text}'")
    return jsonify({'response': response_text})

  except Exception as e:
    print(f"Error during text generation: {e}")
    return jsonify({'error': f'Failed to generate text: {str(e)}'}), 500

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)