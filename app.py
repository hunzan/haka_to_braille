import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from converter import convert_text_to_braille

# 載入環境變數
load_dotenv()

# 建立 Flask app
app = Flask(__name__, static_folder="static")

# 🔹 主要 API 端點
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    text = data.get("text", "")
    input_type = data.get("inputMode", "haka")

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)