from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import requests
import os
import json
import types

class reactions:

    def __init__(self):
        line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
        ENDPOINT = "https://www.cotogoto.ai/webapi/noby.json"
        API_KEY = '313fbe3c3dd8381b9e26a3a3bc36d51d'

    def get_daily_report(self, event, diary_mode_flag):
        diary_mode_flag = True
        self.line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="どうぞ!"))

        return diary_mode_flag

    def make_picture(self, event, text):
        return

    def reaction_spesific_words(self, event, word_list):
        output = ""
        self.line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output))

    def use_noby(self, event):

        payload = {'text': f'{event.message.text}', 'app_key': self.API_KEY}
        r = requests.get(self.ENDPOINT, params=payload)
        data = r.json()
        response = data["text"]

        self.line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))

    def insert_to_noby_db(self):
        con = sqlite3.connect('./replys.DB')
        cur = con.cursor()
        sql = 'IN'