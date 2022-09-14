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

# from reactions import reactions

# reactions = reactions()

app = Flask(__name__)

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
    # print(event.message.text)
    con = sqlite3.connect('tables.db')
    diary_mode_flag = check_user(con, user_id)
        #deeplに渡す
    received_text = event.message.text
    received_text = translate_lang(received_text,"JA","EN")
    message = "" #返信メッセージ

    if diary_mode_flag == True:
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="画像を生成します"))
        diary_mode_flag = False
        message = "diary image"

        cur = con.cursor()
        # reset flag
        cur.execute('''UPDATE INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], False)
        # TODO:

    else :
        if "dialy" in received_text:
            cur = con.cursor()
            cur.execute('''UPDATE INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], True)
            get_daily_report(event)
        else:
            print("反応モード")
            message = is_matched_full_text(event.message.text, con)
            if message == "":
                message = use_noby(event)

    line_bot_api.reply_message(
    event.reply_token, TextSendMessage(text=message))
    con.close()

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



#########

def is_matched_full_text(message, con):
    cur = con.cursor()
    reply_message = cur.execute('''SELECT REPLY_WORD FROM REPLIES WHERE TARGET_WORD=? ''', [message]).fetchone()
    if reply_message is None:
        return ""
    else:
        return reply_message[0]

def get_daily_report(event, diary_mode_flag):
    diary_mode_flag = True
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="どうぞ!"))

    return diary_mode_flag

# def make_picture(self, event, text):
#     return

# def reaction_spesific_words(self, event, word_list):
#     output = ""
#     self.line_bot_api.reply_message(
#     event.reply_token,
#     TextSendMessage(text=output))

def use_noby(event):
    payload = {'text': f'{event.message.text}', 'app_key': API_KEY_noby}
    r = requests.get(ENDPOINT, params=payload)
    data = r.json()
    response = data["text"]
    #DBに保存 TODO: これは何?
    insert_to_replys_db(target_word=event.message.text, reply_word=response)

    return response


def insert_to_replys_db(target_word, reply_word):
    '''
    '''
    con = sqlite3.connect('replys.DB')
    cur = con.cursor()
    sql = 'INSERT INTO REPLIES (target_word, reply) values (?, ?)'
    data = [target_word, reply_word]
    cur.execute(sql, data)
    con.commit()
    con.close()

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
    # {'translations': [{'detected_source_language': 'EN', 'text': 'リーマンゼータ関数は、整数論において非常に重要な関数である。'}]}
    return result['translations'][0]['text']

def check_user(con, user_id):
    cur = con.cursor()
    try :
        cur.execute('''INSERT INTO USERS(USERID, DIARYMODEFLAG) VALUES(?, ?)''', [user_id], False)
        diary_mode_flag = False
    except sqlite3.IntegrityError as e:
        diary_mode_flag = cur.execute('''SELECT DIARYMODEFLAG FROM USERS WHERE USERID=? ''', [user_id]).fetchone()[0]
        print(diary_mode_flag)
    return diary_mode_flag


if __name__ == "__main__":
    print(transralte_lang("こんにちは","JA","EN"))
    con = sqlite3.connect('tables.db')
    print(is_matched_full_text("hello",con))
    print(is_matched_full_text("ooo", con))

    con.close()
