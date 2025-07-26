import os
import json
import re
from dotenv import load_dotenv

# ✅ 放在最前面！先定義資料夾路徑
DATA_DIR = os.path.join(os.path.dirname(__file__), 'braille_data')

# ✅ 檔案路徑定義
CONSONANTS_HPZT_FILE = os.path.join(DATA_DIR, 'consonants_hpzt.json')  # 海陸、大埔、饒平、詔安
CONSONANTS_SIIAN2_FILE = os.path.join(DATA_DIR, 'consonants_siian2.json')  # 四縣、南四縣
VOWELS_FILE = os.path.join(DATA_DIR, 'vowels.json')
RUSHIO_FILE = os.path.join(DATA_DIR, 'rushio_syllables.json')
TONE_HPZT_FILE = os.path.join(DATA_DIR, 'tone_hpzt.json')
TONE_SIIAN2_FILE = os.path.join(DATA_DIR, 'tone_siian2.json')

load_dotenv()

# ✅ 全域變數初始化
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ✅ 2. 自動分音節函式 ← 林北建議放這裡
def split_syllables_auto(text, tones, rushio):
    # 1. 取出所有 tone 符號做成 pattern
    tone_marks = sorted(tones.keys(), key=len, reverse=True)
    escaped_marks = [re.escape(mark) for mark in tone_marks if mark]
    tone_pattern = f"(?:{'|'.join(escaped_marks)})?"

    # 2. rushio 先處理：音節不加 tone 符號
    rushio_keys = sorted(rushio.keys(), key=len, reverse=True)
    rushio_pattern = '|'.join(re.escape(k) for k in rushio_keys)

    # 3. 其他拼音音節：允許接 tone 符號
    normal_pattern = f"[a-zA-Z]+{tone_pattern}"

    # 4. 總 pattern：rushio 在前（優先），再一般拼音
    pattern = re.compile(f"({rushio_pattern}|{normal_pattern})")

    return [m.group(0) for m in pattern.finditer(text)]

def parse_syllable(syll, consonants, vowels, tones, rushio, dialect):
    sixth_dot = ""

    syll = syll.strip()

    # ✅ 特例：跳過 ii，處理 iin / iim（含子音開頭情況）
    base_syll = syll
    tone_mark = ""
    for mark in tones:
        if mark and mark in base_syll:
            tone_mark = mark
            base_syll = base_syll.replace(mark, "")
            break

    if base_syll.endswith("iim") or base_syll.endswith("iin"):
        if base_syll.endswith("iim"):
            base = base_syll[:-3]
            coda = "m"
        else:
            base = base_syll[:-3]
            coda = "n"

        parts = [sixth_dot] if sixth_dot else []

        # 有子音的情況
        if base:
            if base in consonants:
                parts.append(get_dots(consonants, base))
            else:
                return "⍰"  # 無效子音
        # 無子音（單獨 iim / iin）
        parts.append(get_dots(consonants, coda))

        if tone_mark:
            parts.append(get_dots(tones, tone_mark))
        else:
            parts.append("⠤")  # 無 tone 時補上 ⠤

        return ''.join(parts)

    # 先把音調符號抽出（入聲不需加音調，先標記 tone_mark）
    tone_mark = ""
    for mark in tones.keys():
        if mark and mark in syll:
            tone_mark = mark
            syll = syll.replace(mark, "")
            break

    # 詔安腔 nn 特殊處理，加第六點標記
    if dialect == "詔安" and syll.endswith("nn"):
        sixth_dot = "⠠"
        syll = syll[:-2]

    # 判斷 syll 是否為 rushio（入聲），入聲不加音調
    if syll in rushio:
        return sixth_dot + get_dots(rushio, syll)

    # 嘗試拆解：子音 + rushio（入聲）
    for r in sorted(rushio.keys(), key=lambda x: -len(x)):
        if syll.endswith(r):
            onset = syll[:-len(r)]
            if onset in consonants:
                return sixth_dot + get_dots(consonants, onset) + get_dots(rushio, r)

    # 嘗試母音 vowels
    if syll in vowels:
        parts = [sixth_dot, get_dots(vowels, syll)]
        if tone_mark in tones:
            parts.append(get_dots(tones, tone_mark))
        return ''.join(parts)

    # 嘗試拆解正常音節（子音 + 母音 + coda）
    onset, nucleus, coda = "", "", ""
    remainder = syll

    for c in sorted(consonants.keys(), key=len, reverse=True):
        if remainder.startswith(c):
            onset = c
            remainder = remainder[len(c):]
            break

    for v in sorted(vowels.keys(), key=len, reverse=True):
        if remainder.startswith(v):
            nucleus = v
            coda = remainder[len(v):]
            break
    else:
        # 單音 m, n, ng 可能在此被判斷失敗，所以等會特別處理
        pass

    # ✅ 一開始就預設 is_rushio
    is_rushio = False

    # 若有找到母音，繼續組合
    if nucleus:
        parts = [sixth_dot]
        if onset:
            parts.append(get_dots(consonants, onset))
        parts.append(get_dots(vowels, nucleus))

        if coda:
            if coda in rushio:
                parts.append(get_dots(rushio, coda))
                is_rushio = True
            elif coda in consonants:
                parts.append(get_dots(consonants, coda))
            else:
                return "⍰"

        # ✅ tone 處理：只有不是入聲才會處理 tone
        if not is_rushio:
            if tone_mark:
                parts.append(get_dots(tones, tone_mark))
            else:
                parts.append("⠤")  # 無聲調 → 補 ⠤

        return ''.join(parts)

    # **最後處理單音 m, n, ng （子音或母音）**
    if syll in ["m", "n", "ng"]:
        parts = [sixth_dot]
        if syll in vowels:
            parts.append(get_dots(vowels, syll))
        elif syll in consonants:
            parts.append(get_dots(consonants, syll))
        else:
            return "⍰"
        if tone_mark in tones:
            parts.append(get_dots(tones, tone_mark))
        else:
            parts.append("⠤")
        return ''.join(parts)

    # 其他狀況返回錯誤符號
    return "⍰"

def get_dots(dictionary, key):
    return dictionary.get(key, {}).get("dots", "")

def convert_text_to_braille(text, dialect):
    if dialect in ["四縣", "南四縣"]:
        consonants = load_json(CONSONANTS_SIIAN2_FILE)
        tones = load_json(TONE_SIIAN2_FILE)
    elif dialect in ["海陸", "大埔", "饒平", "詔安"]:
        consonants = load_json(CONSONANTS_HPZT_FILE)
        tones = load_json(TONE_HPZT_FILE)
    else:
        return "⚠️ 無效腔調：請選擇有效的客語腔調"

    vowels = load_json(VOWELS_FILE)
    rushio = load_json(RUSHIO_FILE)

    lines = text.splitlines()
    final_lines = []

    for line in lines:
        # ✅ 改這裡：支援 toiˇvanˇnginˇ 無空格也能切音節
        syllables = split_syllables_auto(line.strip(), tones, rushio)
        braille_line = []

        for syll in syllables:
            result = parse_syllable(syll, consonants, vowels, tones, rushio, dialect)
            if result:
                braille_line.append(result)
            else:
                braille_line.append("⍰")  # 轉換失敗用符號標記

        final_lines.append(" ".join(braille_line))

    return "\n".join(final_lines)