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



app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

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
def handle_message(event):
    con = sqlite3.connect('tables.db')
    message = is_matched_full_text(event.message.text, con)
    if message != "":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))
    else:
        print("no match")
    con.close()
    
    return 'OK'

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