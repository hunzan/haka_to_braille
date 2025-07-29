# 🧩 haka_to_braille  
**台灣客語拼音 ➡ 客語點字轉換工具**  
支援台灣六大客語腔調（四縣、海陸、大埔、饒平、詔安、南四縣）

---

## 📌 簡介

`haka_to_braille` 是一個專為視障人士與語言學習者設計的點字轉換工具，可將 **台灣客語拼音** 自動解析並轉換為對應的 **客語點字**。  
此工具支援「入聲」、「聲調」、「詔安腔鼻音 nn」等複雜語言邏輯，使用者可選擇需要的腔調做正確轉換。

本工具的點字規則參照台灣苗栗視障巡迴輔導教師李文煥老師研發的點字規則，日後若經各界專家學者再行討論研議相關規則，屆時再予補充調整。

---

## 🎯 功能特色

- ✅ 支援多腔調：四縣、海陸、大埔、饒平、詔安、南四縣
- ✅ 精準解析入聲、聲調、自帶音調處理
- ✅ 支援鼻音標記（nn → 第六點 ⠠）
- ✅ 支援拼音變形處理（如 `iin` / `iim` 的簡化）
- ✅ 自動分音節與處理 tone mark
- ✅ 可供無障礙教育、語言學習、點字出版應用

---

## 🚀 使用方式

### 1️⃣ 安裝相依套件（可選）

pip install python-dotenv

### 2️⃣ 執行主轉換程式

請參見 convert_text_to_braille(text, dialect) 函式

---

## 🗂️ 專案架構

haka_to_braille_converter/
├── app.py
├── converter.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── script.js
│   ├── styles.css
│   └── favicon.ico
├── braille_data/
│   ├── consonants_hpzt.json
│   ├── consonants_siian2.json
│   ├── vowels.json
│   ├── rushio_syllables.json
│   ├── tone_hpzt.json
│   └── tone_siian2.json   
└── README.md

---

## 🛠️ 開發與貢獻

本專案由定向行動兼生活技能訓練老師/本土語文推廣者/vibe-coder 阿猴（A-kâu）＆ 金蕉（Kim-chio）合作開發

結合台灣視障點字教育與本土語言專業研發之線上工具，致力於讓點字使用者也能接觸多元母語。

歡迎使用者提出建議與改進。請確保：

語音處理邏輯符合腔調規範

JSON 點字資料正確、完整

不影響既有腔調與功能正確性

---

##  📚 參考與致謝

台灣客語拼音系統（教育部）

客語語言學與語音學教材（台灣苗栗視障巡迴輔導教師，台灣客語點字研發者 李文煥老師）

ChatGPT 協作技術輔助與程式設計

---

## 📄 授權 License

MIT License – 歡迎自由使用與修改，請保留原始出處說明。

Copyright © 2025 Lîm Akâu & KimTsio
