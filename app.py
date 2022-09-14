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

from reactions import reactions

reactions = reactions()

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])


# diary_mode_flag = False

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
    user_id = event.source.userId
    # print(event.message.text)
    con = sqlite3.connect('tables.db')
    cur = con.cursor()
    try :
        user = cur.execute('''INSERT INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], False)
        diary_mode_flag = False
    except sqlite3.IntegrityError as e:
        diary_mode_flag = cur.execute('''SELECT DIARYMODEFLAG FROM USERS WHERE USERID=? ''', [user_id]).fetchone()[0]
        print(diary_mode_flag)
    con.close()

    if diary_mode_flag == True:
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
        message = "diary image"

        con = sqlite3.connect('tables.db')
        cur = con.cursor()
        user = cur.execute('''UPDATE INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], False)
        con.close()

    else :
        if "dialy" in event.message.text:
            con = sqlite3.connect('tables.db')
            cur = con.cursor()
            user = cur.execute('''UPDATE INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], True)
            con.close()
            reactions.get_daily_report(event)
        else:
            print("反応モード")
            #word_list:登録しているworde ega
            con = sqlite3.connect('tables.db')
            message = reactions.is_matched_full_text(event.message.text, con)
            if message == "":
                reactions.use_noby(event)

            con.close()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))

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
