這是一個將 Chrome 擴充功能與 Colab 上的 Flask API 服務結合，用來偵測當前網站 URL 的專案。

<div class="notes-section">

📝 注意事項與執行步驟總覽
ngrok 設定：在 ngrok 官網創建帳號並取得 Authtoken，用於 Colab 程式碼中。

Colab 執行：先在 Colab 運行 Python 程式碼，取得 PUBLIC URL。

本地檔案修改：將取得的 PUBLIC URL 貼入本地的 popup.js 檔案中。

載入擴充功能：在 Chrome 擴充功能頁面載入本地專案資料夾。

CORS 處理：後端 Colab 程式碼已加入 flask-cors 和 OPTIONS 請求處理，以解決跨域問題。

</div>

💻 本地 Chrome 擴充功能檔案
請將以下三個檔案放在同一個資料夾，並確保您有 icon.png 檔案（或刪除 manifest.json 中相關配置）。

1. manifest.json
JSON

{
  "manifest_version": 3,
  "name": "釣魚網站偵測器",
  "version": "1.0",
  "description": "將網址送到 Colab API 判斷是否為釣魚網站",
  "host_permissions": ["<all_urls>"],
  "permissions": ["tabs"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icon.png",
      "48": "icon.png",
      "128": "icon.png"
    }
  }
}
2. popup.html
HTML

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>釣魚網站偵測</title>
  <style>
    body { font-family: Arial; width: 250px; padding: 10px; }
  </style>
</head>
<body>
  <h3>正在偵測當前網站...</h3>
  <p id="result">請稍候</p>

  <script src="popup.js"></script>
</body>
</html>
3. popup.js
程式碼片段

document.addEventListener("DOMContentLoaded", () => {
  const resultEl = document.getElementById("result");
  // 🚨 替換為 Colab 程式碼運行後輸出的 PUBLIC URL
  const ngrokUrl = "https://d84d-35-230-74-117.ngrok-free.app"; 

  // ⛳ 取得目前活動頁面的網址
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (!tabs || tabs.length === 0) {
      resultEl.textContent = "無法取得目前分頁";
      return;
    }

    const url = tabs[0].url;

    if (!url) {
      resultEl.textContent = "目前分頁網址為空";
      return;
    }

    // ✅ 呼叫 ngrok API
    try {
      const response = await fetch(`${ngrokUrl}/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        throw new Error(`API 請求失敗，狀態碼: ${response.status}`);
      }

      const data = await response.json();
      resultEl.textContent = "判斷結果：" + data.message;
    } catch (err) {
      resultEl.textContent = "錯誤：" + err.message;
    }
  });
});
🐍 Colab 後端程式碼 (Flask + ngrok)
請在 Google Colab 中執行以下程式碼。執行後請務必將輸出的 PUBLIC URL 貼到本地的 popup.js 中。

程式碼片段

!pip install pyngrok flask  # 換用 pyngrok，比 flask_ngrok 穩定 
!pip install flask-cors

from pyngrok import ngrok
from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ 處理跨域來源問題


# 1️⃣ 指定 ngrok authtoken
# 🚨 請替換成您自己的 Authtoken！
ngrok.set_auth_token('2zHr1TSVQF5zwvUezbLLGVSnoxD_4hZVw8ah1tNaG6ifn2eVq')

# 2️⃣ 手動開一條隧道
public_url = ngrok.connect(5000, "http")    # 先開 5000 埠
print("PUBLIC URL:", public_url) # 🔔 記下這個網址，填入 popup.js

# 3️⃣ 再啟動 Flask
app = Flask(__name__)
# ✅ 啟用 CORS，允許所有來源（*）跨域存取
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route("/check", methods=["POST", "OPTIONS"])
def check():
    if request.method == "OPTIONS":
        # ✅ 明確回應預檢請求，避免 CORS 擋下正式請求
        return '', 204

    # 處理正式 POST 請求
    data = request.get_json()
    url = data.get("url", "")
    return jsonify({"message": f"你送來的網址是：{url}"})

app.run(port=5000)
