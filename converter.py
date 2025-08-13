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

# ✅ 自動分音節（tokenizer）
# 依「當前腔調 rushio 檔」之鍵名（自帶 tone）最長優先 → 先抓成套入聲音節
def split_syllables_auto(text, tones, rushio):
    # 1) rushio 鍵最長優先（自帶 tone 的整音節，如 iabˋ / ag / id / iogˋ ...）
    rushio_keys = sorted(rushio.keys(), key=len, reverse=True)
    rushio_pattern = '|'.join(re.escape(k) for k in rushio_keys) if rushio_keys else r"(?!x)x"

    # 2) 一般拼音 + 可選 tone（tone 自 tones.json，最長優先）
    tone_marks = sorted([k for k in tones.keys() if k], key=len, reverse=True)
    escaped_marks = [re.escape(mark) for mark in tone_marks]
    tone_pattern = f"(?:{'|'.join(escaped_marks)})?"

    # 拼音主體：連續字母 + 可選 tone
    normal_pattern = f"[A-Za-z]+{tone_pattern}"

    # 3) 標點
    punctuation_chars = r"，,。.？?！!：:；;、「“」”『‘』’（(）)【[】]《{》}—‧…"
    punctuation_pattern = f"[{re.escape(punctuation_chars)}]"

    # ✅ 順序：rushio（帶調整音節） → 一般拼音 → 標點
    full_pattern = re.compile(f"({rushio_pattern}|{normal_pattern}|{punctuation_pattern})")
    return [m.group(0) for m in full_pattern.finditer(text)]

def parse_syllable(syll, consonants, vowels, tones, rushio, dialect):
    sixth_dot = ""
    s = syll.strip()

    # 1) 鼻化：nn → 第六點，並移除 nn 以利後續處理
    if "nn" in s:
        sixth_dot = "⠠"
        s = s.replace("nn", "")

    # 2) 先處理「帶調的 rushio 整音節」（rushio 自帶 tone → 不再附加 tone）
    if s in rushio:
        dots = get_dots(rushio, s)
        return (sixth_dot + dots) if sixth_dot else dots

    # 3) 先剝 tone（最長優先），保留原 s（含 tone）給後面子音+rushio 判斷
    tone_mark = ""
    base = s
    for mark in sorted([k for k in tones if k], key=len, reverse=True):
        if mark and mark in base:
            tone_mark = mark
            base = base.replace(mark, "")
            break

    # 4) 特例：iim / iin
    if base.endswith("iim") or base.endswith("iin"):
        body = base[:-3]
        coda_cons = "m" if base.endswith("iim") else "n"
        parts = [sixth_dot] if sixth_dot else []
        if body:
            if body in consonants:
                parts.append(get_dots(consonants, body))
            else:
                return "⍰"
        parts.append(get_dots(consonants, coda_cons))
        parts.append(get_dots(tones, tone_mark) if tone_mark else "⠤")
        return "".join(parts)

    # 5) 詔安腔額外 nn 相容處理（若仍有殘留）
    if dialect == "詔安" and base.endswith("nn"):
        sixth_dot = "⠠"
        base = base[:-2]

    # 6) 「子音 + rushio」：只接受『帶調鍵』（用 s 而非 base 來比）
    for r in sorted(rushio.keys(), key=len, reverse=True):
        if s.endswith(r):  # r 例：'idˋ', 'agˋ', 'edˋ'（鍵名含調）
            onset = s[:-len(r)]
            if onset in consonants:
                parts = [sixth_dot] if sixth_dot else []
                parts.append(get_dots(consonants, onset))
                parts.append(get_dots(rushio, r))  # rushio 自帶 tone
                return "".join(parts)

    # ===== 進入「鎖定韻母」流程 =====
    cons_keys  = sorted(consonants.keys(), key=len, reverse=True)
    vowel_keys = sorted(vowels.keys(),     key=len, reverse=True)

    # 6.1 取最長起首子音（可為空）
    onset = ""
    rest = base
    for c in cons_keys:
        if rest.startswith(c):
            onset = c
            rest = rest[len(c):]
            break

    # 6.2 必須在當前 rest 開頭「一次」匹配到最長韻母，鎖定之
    rime = ""
    for v in vowel_keys:
        if rest.startswith(v):
            rime = v
            rest = rest[len(v):]   # 之後內容視為「外加尾綴」
            break
    if not rime:
        # 沒有韻母 → 嘗試單音節 m/n/ng
        if base in ["m", "n", "ng"]:
            parts = [sixth_dot] if sixth_dot else []
            if base in vowels:
                parts.append(get_dots(vowels, base))
            elif base in consonants:
                parts.append(get_dots(consonants, base))
            else:
                return "⍰"
            parts.append(get_dots(tones, tone_mark) if tone_mark else "⠤")
            return "".join(parts)
        return "⍰"

    parts = [sixth_dot] if sixth_dot else []
    if onset:
        parts.append(get_dots(consonants, onset))
    parts.append(get_dots(vowels, rime))   # 韻母鎖定

    # 6.3 處理「外加尾綴」
    if rest:
        # (a) 優先嘗試『尾綴+tone』是否剛好是 rushio 的帶調鍵
        rest_toned = (rest + tone_mark) if tone_mark else rest
        if rest_toned in rushio:
            parts.append(get_dots(rushio, rest_toned))  # 自帶 tone
            return "".join(parts)

        # （相容舊資料）若需要，也可接受無調鍵
        if rest in rushio:
            parts.append(get_dots(rushio, rest))  # 自帶 tone（由點字定義）
            return "".join(parts)

        # (b) 否則僅允許純子音尾綴（逐段最長匹配）
        tail = rest
        while tail:
            matched = False
            for c in cons_keys:
                if tail.startswith(c):
                    parts.append(get_dots(consonants, c))
                    tail = tail[len(c):]
                    matched = True
                    break
            if not matched:
                return "⍰"  # 既不是 rushio 也不是純子音序列 → 無效
        # 吃完全部子音尾綴 → 之後仍可加 tone
        parts.append(get_dots(tones, tone_mark) if tone_mark else "⠤")
        return "".join(parts)

    # (尾綴為空) 正常加 tone
    parts.append(get_dots(tones, tone_mark) if tone_mark else "⠤")
    return "".join(parts)

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
        # ✅ 這裡使用「當前腔調 rushio 鍵（自帶 tone）最長優先」來粗切
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

                # 🆕 特例：原文「 轉成點字 ⠦ 後面不加空格
                if braille_punct == "⠦" and syll == "「":
                    braille_line += braille_punct
                    continue

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

                # 🆕 句末點字符號（⠲ .／。 、⠖ !／！ 、⠦ ?／？）
                #    一般情況後面補一顆點字空格；但若下一個是結束型標點（ ） 」 』 】 ），則不補
                if braille_punct in {"⠲", "⠖", "⠦"}:
                    next_token = syllables[idx + 1] if idx + 1 < syll_count else None
                    closing_no_space = {"）","）",")","」","』","】","]"}
                    if next_token not in closing_no_space:
                        if not braille_line.endswith(braille_space):
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

        # 三個句點（省略號）後補一個點字空格（避免黏住）
        braille_line = re.sub(r'(⠲⠲⠲)(?!\u2800)', r'\1' + "\u2800", braille_line)

        final_lines.append(braille_line.strip())

    return "\n".join(final_lines)
