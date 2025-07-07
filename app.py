import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from converter import convert_text_to_braille
from line_bot import line_callback  # 如果你有 LINE Bot 的話，要記得引入

# 載入環境變數
load_dotenv()

# 建立 Flask app
app = Flask(__name__, static_folder="static")

# 註冊 LINE Bot Webhook 路由（如果有）
app.add_url_rule('/callback', view_func=line_callback, methods=['POST'])

# 🔹 主要 API 端點
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    text = data.get("text", "")
    input_type = data.get("inputMode", "tl")

    final_output = convert_text_to_braille(text, input_type)

    return jsonify({"braille": final_output})

# 🔹 首頁（前端介面）
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 處理 /favicon.ico 避免 404 錯誤
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/support_us')
def support_us():
    return render_template('support_us.html')

@app.route("/ncp/api/create-order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()  # 取前端傳來的資料
        print("收到訂單資料：", data)

        # 🔸 這裡應該要呼叫 PayPal 的 API 建立訂單（等你後續串接）
        # 先假裝建立訂單成功，給個假的訂單 ID
        order_id = "FAKE_ORDER_ID_12345"

        # 回傳訂單 ID（前端會用這個）
        return jsonify({"id": order_id})
    except Exception as e:
        print("建立訂單時發生錯誤：", e)
        return jsonify({"error": "建立訂單失敗"}), 500

# 🔹 啟動 Flask 伺服器（開發用）
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
