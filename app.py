from email import message
from flask import Flask, request, abort, render_template

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)
import os
import sqlite3
from flask import g
import random
from flask_bootstrap import Bootstrap
import requests
import json
import types
import cld3

app = Flask(__name__)
bootstrap = Bootstrap(app)
line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

# noby
ENDPOINT = "https://www.cotogoto.ai/webapi/noby.json"
API_KEY_noby = '313fbe3c3dd8381b9e26a3a3bc36d51d'

#deepl
API_KEY_dl = '0210a084-8bd5-b5cb-af38-e2f2bbfb9a2a:fx' # 自身の API キーを指定

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
    user_id = event.source.user_id
    con = sqlite3.connect('tables.db')

    diary_mode_flag = check_user(con, user_id)
        #deeplに渡す
    received_text = event.message.text
    message = "" #返信メッセージ

    if diary_mode_flag == 1:
        received_text = transralte_lang(received_text, "JA", "EN")

        # request = requests.get("https://aws.random.cat/meow")
        request = requests.get("https://dog.ceo/api/breeds/image/random")
        request = request.json()

        image_url = request['message']

        diary_mode_flag = 0
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        message = "But that doesn't matter, look at my friends!"

        cur = con.cursor()
        # reset flag
        cur.execute('''UPDATE USERS SET DIALY_MODE_FLAG = ? WHERE USERID = ?''', (0, user_id,))
        con.commit()

    else :
        if ("dialy" in received_text) or ("日記" in received_text):
            cur = con.cursor()
            cur.execute('''UPDATE USERS SET DIALY_MODE_FLAG = ? WHERE USERID = ?''', (1, user_id))
            con.commit()

            message = "Let me hear it!"

        elif ("help" in received_text) or ("使い方" in received_text):
            message = "I'll introduce myself!\n自己紹介するよ！\n\n1. I'll answer anything to your message!\n1. あなたのメッセージに対してなんでも答えるよ！\n\n2. If you send me a message including your diary, I will make an image for it!\n2. 日記を含むメッセージをくれると，日記に対して画像を作るよ！\n\n3. Every once in a while I'll send you a message to encourage you or make you smile!\n3. たまにあなたを励ましたり，笑顔にするメッセージを送信するよ！"

        else:
            message = is_matched_full_text(event.message.text, con)
            if message == "":
                message = use_noby(con, event)

    line_bot_api.reply_message(
    event.reply_token, TextSendMessage(text=message))
    con.close()

    return 'OK'

#マニュアルメッセージ
@app.route("/send/<message>")
def push_manual_message(message):
    line_bot_api.broadcast([TextSendMessage(text=message)])

    return 'OK'

#プッシュメッセージ
@app.route("/send")
def push_message():
    con = sqlite3.connect('tables.db')
    cur = con.cursor()
    messages = cur.execute('''SELECT * FROM MESSAGES''').fetchall()
    line_bot_api.broadcast([TextSendMessage(text=random.choice(messages)[0])])
    con.close()

    return 'OK'

#プッシュメッセージ
@app.route("/send/advice")
def push_advice():
    request = requests.get("https://api.adviceslip.com/advice")
    request = request.json()
    line_bot_api.broadcast([TextSendMessage(text=request['slip']['advice'])])

    return 'OK'

#プッシュメッセージ
@app.route("/send/joke")
def push_joke():
    request = requests.get("https://icanhazdadjoke.com/slack", {"Accept": "text/plain"})
    request = request.json()
    line_bot_api.broadcast([TextSendMessage(text=request['attachments'][0]['text'])])

    return 'OK'

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
        return form()

#########

def is_matched_full_text(message, con):
    cur = con.cursor()
    reply_message = cur.execute('''SELECT REPLY_WORD FROM REPLIES WHERE TARGET_WORD=? ''', [message]).fetchone()
    if reply_message is None:
        return ""
    else:
        return reply_message[0]

def use_noby(con, event):
    input_text = event.message.text
    #言語の確認
    use_lang = chek_lang(input_text)
    #transrate to JA
    input_text = transralte_lang(input_text, "EN", "JA")
    payload = {'text': f'{input_text}', 'app_key': API_KEY_noby}
    r = requests.get(ENDPOINT, params=payload)
    data = r.json()
    response = data["text"]
    #DBに保存 TODO: これは何?
    if use_lang == "en":
        response = transralte_lang(response, "JA", "EN")

    return response

def insert_to_replys_db(con, target_word, reply_word):
    '''
    '''
    cur = con.cursor()
    sql = '''INSERT INTO REPLIES (TARGET_WORD, REPLY_WORD) values (?, ?)'''
    data = [target_word, reply_word]
    cur.execute(sql, data)
    con.commit()

def transralte_lang(text, source_lang, target_lang):
    """
    return: deeplからの返り値
    """
    # パラメータの指定
    params = {
                'auth_key' : API_KEY_dl,
                'text' : text,
                'source_lang' : source_lang, # 翻訳対象の言語
                "target_lang": target_lang  # 翻訳後の言語
            }
    # リクエストを投げる
    request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
    result = request.json()
    return result['translations'][0]['text']

def check_user(con, user_id):
    cur = con.cursor()

    diary_mode_flags = cur.execute('''SELECT DIALY_MODE_FLAG FROM USERS WHERE USERID=? ''', (user_id,)).fetchone()

    if diary_mode_flags == None:
        cur.execute('''INSERT INTO USERS(USERID, DIALY_MODE_FLAG) VALUES(?, ?)''', (user_id, 0))
        con.commit()
        diary_mode_flag = 0
    else :
        diary_mode_flag = diary_mode_flags[0]
        print(diary_mode_flag)
    return diary_mode_flag

def chek_lang(text):
    cld3_languages = cld3.get_frequent_languages(
        text,
        num_langs=3,
        )
    use_lang = "en"
    for i in cld3_languages:
        print(i)
        if i[0] == "ja":
            use_lang = "ja"
            break

    return use_lang

if __name__ == "__main__":
    app.run()