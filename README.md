# 台羅拼音轉台語點字線上工具（TJ to Taigu/Taigi Braille Converter on Web）

## 開發者
Lîm Akâu（林阿猴） & KimTsio（金蕉）

## 使用方式
1. **輸入方式**：請輸入台羅拼音的正常聲調標示方式，**不使用數字調號**。
   - 範例：`guá sī tâi-uân-lâng`
2. **輸入規範**：
   - 一律使用 **小寫字母輸入**。
   - **組合字詞請使用連字符 `-`**。
   - 標點符號目前尚無統一點字規則，請以空格分隔。

## 系統需求
- Python 3.10 以上
- 套件需求：詳見 `requirements.txt`

## 啟動方式
```bash
# 安裝相依套件
pip install -r requirements.txt

# 啟動伺服器
python app.py
```
然後用瀏覽器開啟：http://localhost:5000

## 版權與使用條款
本專案為**免費軟體**，僅供學術、教育與非營利用途。

**禁止任何形式的商業利用。**

點字轉換邏輯與介面設計仍在持續優化中，若有建議歡迎提出 Issue。

---
Copyright © 2025 Lîm Akâu & KimTsio
