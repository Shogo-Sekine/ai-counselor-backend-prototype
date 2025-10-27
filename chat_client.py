import requests
import json

API_URL = "http://localhost:5001/generate"

def chat_with_ai(prompt):
  headers = {"Content-Type": "application/json"}
  payload = {"text": prompt}
  try:
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status() # HTTPエラーがあった場合に例外を発生させる
    result = response.json()
    return result.get("response", "エラー: 応答がありません。")
  except requests.exceptions.RequestException as e:
    return f"API接続エラー: {e}"
  except json.JSONDecodeError:
    return f"API応答エラー: JSONデコードに失敗しました。\n応答内容: {response.text}"

if __name__ == "__main__":
    print("AIカウンセラープロトタイプへようこそ！ (終了するには 'exit' または 'quit' と入力)")
    while True:
      user_input = input("あなた: ")
      if user_input.lower() in ["exit", "quit"]:
        print("AI: さようなら！")
        break
      
      print("AI: 考え中...")
      ai_response = chat_with_ai(user_input)
      print(f"AI: {ai_response}")