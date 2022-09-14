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

class diary :
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
def handle_message(event, self):
    print(event.message.text)

    if diary.diary_mode_flag == True:
        print("make_picture")
    # if "diary" in event.message.text:
    #     print(diary_mode_flag)
    #     if not diary_mode_flag :
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text="どうぞ"))

    #         diary_mode_flag = True

    #         #deepl
    #     else:
    #         diary_mode_flag = True
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text="作成中"))

    #         # line_bot_api.reply_message(
    #         #     event.reply_token,
    #         #     TextSendMessage(text="作成中"))

    else :
        if "日記" in event.message.text:
            diary.diary_mode_flag = True
            print("日記を受け付ける")

        else:
            print("反応モード")
            #word_list:登録しているword
            word_list = []
            if event.message.text in word_list:
                print("特定のワードを返す")
                output = ""
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=output))

            else:
                print("nobyに頼る")
                ENDPOINT = "https://www.cotogoto.ai/webapi/noby.json"
                MY_KEY = '313fbe3c3dd8381b9e26a3a3bc36d51d'

                payload = {'text': f'{event.message.text}', 'app_key': MY_KEY}
                r = requests.get(ENDPOINT, params=payload)
                data = r.json()
                response = data["text"]

                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response))

#プッシュメッセージ
@app.route("/send")
def push_message():
    con = sqlite3.connect('messages.db')
    cur = con.cursor()
    messages = cur.execute('''SELECT * FROM MESSAGES''').fetchall()
    line_bot_api.broadcast([TextSendMessage(text=random.choice(messages)[0])])
    print(random.choice(messages)[0])
    con.close()

    return 'OK'