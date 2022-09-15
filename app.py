from flask import Flask, request, abort

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
import requests
import json
import types
import cld3

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


# diary_mode_flag = 0

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
    # print(event.source.user_id)
    user_id = event.source.user_id
    con = sqlite3.connect('tables.db')

    # cur = con.cursor()
    # print(cur.execute('''SELECT DIALY_MODE_FLAG FROM USERS WHERE USERID=? ''', (user_id,)).fetchall())

    diary_mode_flag = check_user(con, user_id)
        #deeplに渡す
    received_text = event.message.text
    # received_text = transralte_lang(received_text,"JA","EN")
    message = "" #返信メッセージ

    # sended_text = transralte_lang(sended_text,"JA","EN")
    if diary_mode_flag == 1:
        # line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text="create figure"))
        received_text = transralte_lang(received_text, "JA", "EN")

        # request = requests.get("https://aws.random.cat/meow")
        request = requests.get("https://dog.ceo/api/breeds/image/random")
        # request = requests.get("https://joeschmoe.io/api/v1/random")
        request = request.json()

        # print(request)

        image_url = request['message']

        diary_mode_flag = 0
        line_bot_api.push_message(user_id, TextSendMessage(text="Image creating"))
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        message = "Image created"

        cur = con.cursor()
        # reset flag
        cur.execute('''UPDATE USERS SET DIALY_MODE_FLAG = ? WHERE USERID = ?''', (0, user_id,))
        con.commit()

    else :
        if "dialy" in received_text:
            cur = con.cursor()
            cur.execute('''UPDATE USERS SET DIALY_MODE_FLAG = ? WHERE USERID = ?''', (1, user_id))
            con.commit()
            # print(cur.execute('''SELECT DIALY_MODE_FLAG FROM USERS WHERE USERID=? ''', (user_id,)).fetchall())

            # get_daily_report(event)
            message = "come on!"

        else:
            print("反応モード")
            message = is_matched_full_text(event.message.text, con)
            if message == "":
                message = use_noby(con, event)

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

# def get_daily_report(event, diary_mode_flag):
#     # diary_mode_flag = 1
#     line_bot_api.reply_message(
#     event.reply_token,
#     TextSendMessage(text="どうぞ!"))

#     return diary_mode_flag

# def make_picture(self, event, text):
#     return

# def reaction_spesific_words(self, event, word_list):
#     output = ""
#     self.line_bot_api.reply_message(
#     event.reply_token,
#     TextSendMessage(text=output))

def use_noby(con, event):
    input_text = event.message.text
    #言語の確認
    use_lang = chek_lang(input_text)
    print(use_lang)
    #transrate to JA
    input_text = transralte_lang(input_text, "EN", "JA")
    payload = {'text': f'{input_text}', 'app_key': API_KEY_noby}
    r = requests.get(ENDPOINT, params=payload)
    data = r.json()
    response = data["text"]
    #DBに保存 TODO: これは何?
    insert_to_replys_db(con, target_word=event.message.text, reply_word=response)
    if use_lang == "en":
        print("----transrate-----")
        response = transralte_lang(response, "JA", "EN")
        print(response)


    return response


def insert_to_replys_db(con, target_word, reply_word):
    '''
    '''
    # con = sqlite3.connect('replys.DB')
    cur = con.cursor()
    sql = '''INSERT INTO REPLIES (TARGET_WORD, REPLY_WORD) values (?, ?)'''
    data = [target_word, reply_word]
    cur.execute(sql, data)
    con.commit()
    # con.close()

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

# def check_user(con, user_id):
#     cur = con.cursor()
#     try :
#         cur.execute('''INSERT INTO USERS(USERID, DIALY_MODE_FLAG) VALUES(?, ?)''', (user_id, 0))
#         diary_mode_flag = 0
#         print("レコードを追加")
#     except sqlite3.IntegrityError as e:
#         diary_mode_flag = cur.execute('''SELECT DIALY_MODE_FLAG FROM USERS WHERE USERID=? ''', (user_id,)).fetchone()[0]
#         print(diary_mode_flag)
#     return diary_mode_flag

def check_user(con, user_id):
    cur = con.cursor()

    diary_mode_flags = cur.execute('''SELECT DIALY_MODE_FLAG FROM USERS WHERE USERID=? ''', (user_id,)).fetchone()

    if diary_mode_flags == None:
        cur.execute('''INSERT INTO USERS(USERID, DIALY_MODE_FLAG) VALUES(?, ?)''', (user_id, 0))
        con.commit()
        diary_mode_flag = 0
        print("レコードを追加")
    else :
        diary_mode_flag = diary_mode_flags[0]
        print(diary_mode_flag)
    return diary_mode_flag

def chek_lang(text):
    cld3_languages = cld3.get_frequent_languages(
        text,
        num_langs=3,
        )
    for i in cld3_languages:
        print(i)
        use_lang = "en"
        if i[0] == "ja":
            use_lang = "ja"

    return use_lang

if __name__ == "__main__":
    # print(transralte_lang("こんにちは","JA","EN"))
    con = sqlite3.connect('tables.db')
    # print(is_matched_full_text("hello",con))
    # print(is_matched_full_text("ooo", con))

    # request = requests.get("https://dog.ceo/api/breeds/image/random")
    #     # request = requests.get("https://joeschmoe.io/api/v1/random")
    # request = request.json()

    # print(request['message'])

    con.close()