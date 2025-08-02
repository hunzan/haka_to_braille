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
PUNCTUATION_FILE = os.path.join(DATA_DIR, 'punctuation.json')

load_dotenv()

# ✅ 全域變數初始化
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ✅ 2. 自動分音節函式 ← 林北建議放這裡
def split_syllables_auto(text, tones, rushio):
    rushio_keys = sorted(rushio.keys(), key=len, reverse=True)
    rushio_pattern = '|'.join(re.escape(k) for k in rushio_keys)

    tone_marks = sorted(tones.keys(), key=len, reverse=True)
    escaped_marks = [re.escape(mark) for mark in tone_marks if mark]
    tone_pattern = f"(?:{'|'.join(escaped_marks)})?"
    normal_pattern = f"[a-zA-Z]+{tone_pattern}"

    # 新增：標點符號正則
    punctuation_chars = r"，,。.？?！!：:；;、「“」”『‘』’（(）)【[】]《{》}—‧…"  # 你也可以從 punctuation.json 載入
    punctuation_pattern = f"[{re.escape(punctuation_chars)}]"

    # rushio 在前，拼音在中，標點在後
    full_pattern = re.compile(f"({rushio_pattern}|{normal_pattern}|{punctuation_pattern})")

    return [m.group(0) for m in full_pattern.finditer(text)]

def parse_syllable(syll, consonants, vowels, tones, rushio, dialect):
    sixth_dot = ""
    syll = syll.strip()

    # ✅ 鼻音：若有 nn，加入第六點，並砍 nn 以利後續處理
    if "nn" in syll:
        sixth_dot = "⠠"
        syll = syll.replace("nn", "")

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
        parts = [sixth_dot] if sixth_dot else []
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
        parts = [sixth_dot] if sixth_dot else []
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
    # 🟢 逗號前空格防呆處理
    text = re.sub(r'\s+(，)', r'\1', text)

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

    punctuation_map = load_json(PUNCTUATION_FILE)

    punct_need_space_after = set("。，．,，：:；;！!」”』’）)】]》}—")
    punct_need_space_before = set("「“『‘（(【[《{")
    sentence_end_punctuations = set("。.！!？?")  # 句子結束符號

    braille_space = "\u2800"  # 點字空格 U+2800

    lines = text.splitlines()
    final_lines = []

    for line in lines:
        syllables = split_syllables_auto(line.strip(), tones, rushio)
        braille_line = ""
        syll_count = len(syllables)

        for idx, syll in enumerate(syllables):
            syll = syll.strip()
            if not syll:
                continue  # 忽略多餘空格

            # 標點處理
            if syll in punctuation_map:
                braille_punct = punctuation_map[syll]

                # 句點符號前永遠不加空格
                if syll in sentence_end_punctuations:
                    braille_line += braille_punct
                else:
                    if syll in punct_need_space_before:
                        if len(braille_line) > 0:
                            braille_line += braille_space
                        braille_line += braille_punct
                    else:
                        braille_line += braille_punct

                    # **核心修正：當標點後面是句點，這標點後面不加空格**
                    if syll in punct_need_space_after:
                        if idx + 1 < syll_count and syllables[idx + 1] in sentence_end_punctuations:
                            pass  # 下一個是句點，不加空格
                        else:
                            braille_line += braille_space
                continue

            # 音節處理
            result = parse_syllable(syll, consonants, vowels, tones, rushio, dialect) or "⍰"
            braille_line += result

            # 判斷 syll 後面是否有原文空格
            next_has_space = False
            is_space_after_tone = False
            if idx + 1 < syll_count:
                inter_text = line.split(syll, 1)[1].split(syllables[idx + 1], 1)[0]
                if " " in inter_text:
                    next_has_space = True
                    # 檢查 syll 是否是 tone 結尾，下一個 syll 是否是拼音
                    if any(tone in syll for tone in tones if tone):
                        next_syll = syllables[idx + 1]
                        if any(c.isalpha() for c in next_syll):  # 下一個是拼音
                            is_space_after_tone = True

            # ...後續決定是否加點字空格時：
            if is_space_after_tone:
                # 音調後的空格 → 不處理（不加點字空格）
                pass
            elif idx + 1 < syll_count and syllables[idx + 1] in sentence_end_punctuations:
                # 句號類符號前不加空格
                pass
            elif next_has_space:
                braille_line += braille_space

        braille_line = re.sub(r'(⠲⠲⠲)(?!\u2800)', r'\1' + "\u2800", braille_line)

        final_lines.append(braille_line.strip())

    return "\n".join(final_lines)

