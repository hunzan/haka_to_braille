import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder="static")

# 🔹 載入 JSON 資料
DATA_DIR = os.path.join(os.path.dirname(__file__), 'braille_data')
CONSONANTS_FILE = os.path.join(DATA_DIR, 'consonants.json')
VOWELS_FILE = os.path.join(DATA_DIR, 'vowels_all.json')
RUSHIO_FILE = os.path.join(DATA_DIR, 'rushio_syllables.json')
NASAL_FILE = os.path.join(DATA_DIR, 'nasal_table.json')

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 🔹 載入 JSON 資料
DATA_DIR = os.path.join(os.path.dirname(__file__), 'braille_data')
CONSONANTS_FILE = os.path.join(DATA_DIR, 'consonants.json')
VOWELS_FILE = os.path.join(DATA_DIR, 'vowels_all.json')
RUSHIO_FILE = os.path.join(DATA_DIR, 'rushio_syllables.json')
NASAL_FILE = os.path.join(DATA_DIR, 'nasal_table.json')

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

consonants = load_json(CONSONANTS_FILE)
vowels = load_json(VOWELS_FILE)
rushio = load_json(RUSHIO_FILE)
nasal = load_json(NASAL_FILE)

# 🔹 切音節函式
def split_syllables(word):
    # 優先使用連字符來斷音節
    return word.split('-')
    result = []
    i = 0

    while i < len(word):
        match = None  # ✅ 初始化匹配變數

        # 先檢查 rushio_syllables 是否獨立匹配
        for r in sorted(rushio.keys(), key=lambda x: -len(x)):
            if word[i:].startswith(r):
                result.append(r)
                i += len(r)
                match = r
                break

        # 再檢查 vowels 是否能獨立匹配
        for v in sorted(vowels.keys(), key=lambda x: -len(x)):
            if word[i:].startswith(v):
                result.append(v)
                i += len(v)
                match = v  # ✅ 確保 match 存的是字串，而非布林值
                break

        # 然後檢查 consonants + vowels / nasal / rushio
        for c in sorted(consonants.keys(), key=lambda x: -len(x)):
            if word[i:].startswith(c):
                for v in sorted(vowels.keys(), key=lambda x: -len(x)):
                    if word[i + len(c):].startswith(v):
                        match = c + v
                        break
                for r in sorted(rushio.keys(), key=lambda x: -len(x)):
                    if word[i + len(c):].startswith(r):
                        match = c + r
                        break
                for n in sorted(nasal.keys(), key=lambda x: -len(x)):
                    if word[i + len(c):].startswith(n):
                        match = c + n
                        break
                if match:
                    result.append(match)
                    i += len(match)
                    break

        if match is None:
            result.append('[錯誤]')
            break

    return result

# 🔹 轉換為點字（包含純母音含聲調處理）
def convert_syllable(s):
    # 直接對應整個音節（完整拼音）優先處理
    if s in nasal:
        return "⠠" + nasal[s]["dots"]
    if s in rushio:
        return rushio[s]["dots"]
    if s in vowels:
        return vowels[s]["dots"]

    # 嘗試分拆子音與母音（或鼻音）
    for c in sorted(consonants.keys(), key=lambda x: -len(x)):
        if s.startswith(c):
            rest = s[len(c):]
            if rest in vowels:
                return consonants[c]["dots"] + vowels[rest]["dots"]
            elif rest in rushio:
                return consonants[c]["dots"] + rushio[rest]["dots"]
            elif rest in nasal:
                return "⠠" + consonants[c]["dots"] + nasal[rest]["dots"]

    # 補上沒聲母的純母音（含聲調）處理
    if s in vowels:
        return vowels[s]["dots"]

    # 無法處理的音節
    return '[錯誤]'

# 🔹 主要 API 端點
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    text = data.get("text", "").strip()

    result_lines = []
    for line in text.splitlines():  # 🔸 分行處理
        result_words = []
        for word in line.split():  # 🔸 每行內分詞
            syllables = split_syllables(word)
            braille = ''.join(convert_syllable(s) for s in syllables)  # ✅ 不要再砍 ⠤
            result_words.append(braille)
        result_lines.append(" ".join(result_words))  # 🔸 該行組合起來

    final_output = "\n".join(result_lines)  # 🔸 回復原始輸入的斷行格式

    return jsonify({"braille": final_output})

# 🔹 首頁（前端介面）
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 處理 /favicon.ico 避免 404 錯誤
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 🔹 啟動 Flask 伺服器
if __name__ == '__main__':
    app.run(debug=True, threaded=True)