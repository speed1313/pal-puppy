from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import sqlite3
from flask import g
import random
import requests
import json
import types

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])


diary_mode_flag = False

@app.route("/")
def test():
    return "<h1>Tests</h1>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event, diary_mode_flag):
    # print(event.message.text)

    if diary_mode_flag == True:
        print("make_picture")
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="画像を生成します"))
        diary_mode_flag = False
        #deeplに渡す
        API_KEY = '0210a084-8bd5-b5cb-af38-e2f2bbfb9a2a:fx' # 自身の API キーを指定
        text = f"{event.message.text}"

        source_lang = 'JA'
        target_lang = 'EN'

        # パラメータの指定
        params = {
                    'auth_key' : API_KEY,
                    'text' : text,
                    'source_lang' : source_lang, # 翻訳対象の言語
                    "target_lang": target_lang  # 翻訳後の言語
                }

        # リクエストを投げる
        request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
        result = request.json()

    else :
        if "日記" in event.message.text:
            diary_mode_flag = True
            print("日記を受け付ける")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="どうぞ"))

        else:
            print("反応モード")
            #word_list:登録しているword

            con = sqlite3.connect('tables.db')
            message = is_matched_full_text(event.message.text, con)
            if message != "":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=message))
            else:
                # print("nobyに頼る")
                ENDPOINT = "https://www.cotogoto.ai/webapi/noby.json"
                MY_KEY = '313fbe3c3dd8381b9e26a3a3bc36d51d'

                payload = {'text': f'{event.message.text}', 'app_key': MY_KEY}
                r = requests.get(ENDPOINT, params=payload)
                data = r.json()
                response = data["text"]

                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response))

            con.close()
            output = ""
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=output))

#プッシュメッセージ
@app.route("/send")
def push_message():
    con = sqlite3.connect('tables.db')
    cur = con.cursor()
    messages = cur.execute('''SELECT * FROM MESSAGES''').fetchall()
    line_bot_api.broadcast([TextSendMessage(text=random.choice(messages)[0])])
    print(random.choice(messages)[0])
    con.close()

    return 'OK'

def is_matched_full_text(message, con):
    cur = con.cursor()
    reply_message = cur.execute('''SELECT REPLY_WORD FROM REPLIES WHERE TARGET_WORD=? ''', [message]).fetchone()
    if reply_message is None:
        return ""
    else:
        return reply_message[0]


if __name__ == "__main__":
    con = sqlite3.connect('tables.db')
    print(is_matched_full_text("hello",con))
    print(is_matched_full_text("ooo", con))

    con.close()
