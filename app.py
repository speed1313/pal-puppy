from flask import Flask, request, abort, render_template

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
from flask_bootstrap import Bootstrap


app = Flask(__name__)
bootstrap = Bootstrap(app)
# line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

line_bot_api = LineBotApi("xx")
handler = WebhookHandler("xx")

@app.route("/")
def test():
    return "<h1>Tests</h1>"

# @app.route("/callback", methods=['POST'])
# def callback():
#     # get X-Line-Signature header value
#     signature = request.headers['X-Line-Signature']

#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # handle webhook body
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         print("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400)

#     return 'OK'


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     con = sqlite3.connect('tables.db')
#     message = is_matched_full_text(event.message.text, con)
#     if message != "":
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=message))
#     else:
#         print("no match")
#     con.close()

#     return 'OK'

# #プッシュメッセージ
# @app.route("/send")
# def push_message():
#     con = sqlite3.connect('tables.db')
#     cur = con.cursor()
#     messages = cur.execute('''SELECT * FROM MESSAGES''').fetchall()
#     line_bot_api.broadcast([TextSendMessage(text=random.choice(messages)[0])])
#     print(random.choice(messages)[0])
#     con.close()

#     return 'OK'

#adminサイト
@app.route("/admin")
def form():
    con = sqlite3.connect('tables.db')
    cur = con.cursor()
    messages = cur.execute(
        '''SELECT MESSAGEID, MESSAGE FROM MESSAGES''').fetchall()
    replies = cur.execute(
        '''SELECT REPLYID, TARGET_WORD, REPLY_WORD FROM REPLIES''').fetchall()
    con.close()

    return render_template('form.html', messages=messages, replies=replies)

#adminサイト  格言追加処理
@app.route('/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        result = request.form
        con = sqlite3.connect('tables.db')
        cur = con.cursor()
        messages = cur.execute('''INSERT INTO MESSAGES(MESSAGE) VALUES(?)''', (result.getlist('register')[0],))
        con.commit()
        con.close()
        # print(result.getlist('register')[0])
        return form()

#adminサイト  格言削除処理
@app.route('/delete', methods = ['POST'])
def delete_message():
    if request.method == 'POST':
        result = request.form
        con = sqlite3.connect('tables.db')
        cur = con.cursor()
        messages = cur.execute(
            '''DELETE FROM MESSAGES WHERE MESSAGEID = ?''', (result.getlist('message_id')[0],))
        con.commit()
        con.close()
        # print(result.getlist('register')[0])
        return form()

#adminサイト  特定のキーワードに対して特定のキーワードを返信する機能   追加処理
@app.route('/keyword_add', methods = ['POST'])
def add_keyword():
    if request.method == 'POST':
        result = request.form
        con = sqlite3.connect('tables.db')
        cur = con.cursor()
        cur.execute('''INSERT INTO REPLIES(TARGET_WORD, REPLY_WORD) VALUES(?, ?)''', ((
            result.getlist('user')[0]), (result.getlist('bot')[0])))
        con.commit()
        con.close()
        # print(result.getlist('register')[0])
        return form()

#adminサイト  特定のキーワードに対して特定のキーワードを返信する機能   削除処理
@app.route('/keyword_del', methods = ['POST'])
def delete_keyword():
    if request.method == 'POST':
        result = request.form
        con = sqlite3.connect('tables.db')
        cur = con.cursor()
        cur.execute('''DELETE FROM REPLIES WHERE REPLYID = ? ''', (result.getlist('reply_id')[0],))
        con.commit()
        con.close()
        # print(result.getlist('register')[0])
        return form()

# def is_matched_full_text(message, con):
#     cur = con.cursor()
#     reply_message = cur.execute('''SELECT REPLY_WORD FROM REPLIES WHERE TARGET_WORD=? ''', [message]).fetchone()
#     if reply_message is None:
#         return ""
#     else:
#         return reply_message[0]


if __name__ == "__main__":
    con = sqlite3.connect('tables.db')
    # print(is_matched_full_text("hello",con))
    # print(is_matched_full_text("ooo", con))

    con.close()
