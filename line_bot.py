import os
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from converter import convert_text_to_braille
from dotenv import load_dotenv

load_dotenv()

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 🔸 記錄使用者輸入模式
user_modes = {}  # {user_id: 'tl' 或 'poj'}


def line_callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip().lower()

    # 🔸 處理指令
    if user_message == "/poj":
        user_modes[user_id] = "poj"
        reply = "✅ 已切換為 POJ 輸入模式"
    elif user_message == "/tl":
        user_modes[user_id] = "tl"
        reply = "✅ 已切換為台羅拼音輸入模式"
    elif user_message == "/mode":
        mode = user_modes.get(user_id, "tl")
        reply = f"目前輸入模式：{'台羅拼音' if mode == 'tl' else 'POJ'}"
    elif user_message == "/help":
        reply = (
            "📄【指令清單】\n"
            "/tl ➜ 切換為台羅拼音模式\n"
            "/poj ➜ 切換為 POJ 模式\n"
            "/mode ➜ 查看目前輸入模式\n"
            "/help ➜ 查看指令說明"
        )
    else:
        # 🔸 正常轉換文字
        input_mode = user_modes.get(user_id, "tl")  # 預設台羅
        result = convert_text_to_braille(user_message, input_mode)
        reply = f"🔸 轉換結果：\n{result}"

    # 🔸 回覆訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

