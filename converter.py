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
    # 不處理 tone 拆解，rushio key 就是含 tone 的拼音（例如 abˋ）
    rushio_keys = sorted(rushio.keys(), key=len, reverse=True)
    rushio_pattern = '|'.join(re.escape(k) for k in rushio_keys)

    # 一般音節：允許含 tone
    tone_marks = sorted(tones.keys(), key=len, reverse=True)
    escaped_marks = [re.escape(mark) for mark in tone_marks if mark]
    tone_pattern = f"(?:{'|'.join(escaped_marks)})?"
    normal_pattern = f"[a-zA-Z]+{tone_pattern}"

    # rushio 在前，優先比對
    pattern = re.compile(f"({rushio_pattern}|{normal_pattern})")
    return [m.group(0) for m in pattern.finditer(text)]

def parse_syllable(syll, consonants, vowels, tones, rushio, dialect):
    sixth_dot = ""
    syll = syll.strip()

    # ✅ 特例：處理 iim / iin（含子音或獨立）
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

        if base:
            if base in consonants:
                parts.append(get_dots(consonants, base))
            else:
                return "⍰"
        parts.append(get_dots(consonants, coda))

        if tone_mark:
            parts.append(get_dots(tones, tone_mark))
        else:
            parts.append("⠤")

        return ''.join(parts)

    # ✅ 詔安腔 nn 特殊處理，加第六點
    if dialect == "詔安" and syll.endswith("nn"):
        sixth_dot = "⠠"
        syll = syll[:-2]

    # ✅ 改：直接用 syll（含 tone）查 rushio
    if syll in rushio:
        return sixth_dot + get_dots(rushio, syll)

    # ✅ 嘗試拆解：子音 + rushio
    for r in sorted(rushio.keys(), key=lambda x: -len(x)):
        if syll.endswith(r):
            onset = syll[:-len(r)]
            if onset in consonants:
                return sixth_dot + get_dots(consonants, onset) + get_dots(rushio, r)

    # ✅ 沒有 match rushio → 現在才拆 tone
    tone_mark = ""
    base_syll = syll
    for mark in tones:
        if mark and mark in base_syll:
            tone_mark = mark
            base_syll = base_syll.replace(mark, "")
            break

    # 嘗試直接查母音
    if base_syll in vowels:
        parts = [sixth_dot, get_dots(vowels, base_syll)]
        if tone_mark in tones:
            parts.append(get_dots(tones, tone_mark))
        else:
            parts.append("⠤")
        return ''.join(parts)

    # 拆解正常音節（子音 + 母音 + coda）
    onset, nucleus, coda = "", "", ""
    remainder = base_syll

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

    is_rushio = False
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

        if not is_rushio:
            if tone_mark:
                parts.append(get_dots(tones, tone_mark))
            else:
                parts.append("⠤")

        return ''.join(parts)

    # 處理單音節 m, n, ng
    if base_syll in ["m", "n", "ng"]:
        parts = [sixth_dot]
        if base_syll in vowels:
            parts.append(get_dots(vowels, base_syll))
        elif base_syll in consonants:
            parts.append(get_dots(consonants, base_syll))
        else:
            return "⍰"
        if tone_mark in tones:
            parts.append(get_dots(tones, tone_mark))
        else:
            parts.append("⠤")
        return ''.join(parts)

    return "⍰"

def get_dots(dictionary, key):
    return dictionary.get(key, {}).get("dots", "")

RUSHIO_FILES = {
    "四縣": "rushio_syllables.json",
    "南四縣": "rushio_syllables.json",
    "海陸": "rushio_syllables.json",
    "饒平": "rushio_syllables.json",
    "大埔": "rushio_tapu.json",
    "詔安": "rushio_choaan.json"
}

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

    rushio_filename = RUSHIO_FILES.get(dialect)
    if not rushio_filename:
        return "⚠️ 無效腔調：請選擇有效的客語腔調"

    rushio_file = os.path.join(DATA_DIR, rushio_filename)
    rushio = load_json(rushio_file)

    lines = text.splitlines()
    final_lines = []

    for line in lines:
        syllables = split_syllables_auto(line.strip(), tones, rushio)
        braille_line = []

        for syll in syllables:
            result = parse_syllable(syll, consonants, vowels, tones, rushio, dialect)
            braille_line.append(result or "⍰")

        final_lines.append(" ".join(braille_line))

    return "\n".join(final_lines)
