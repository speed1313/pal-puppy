# mother-bot
this is a healing line bot for tired people.
We developed this app as a product of a hackathon held at Rakuten Group, Inc. summer intern 2022.

## how to use
Please register this bot as a friend and send a message to it.
This bot's basic ID is @882ctzvj.

This bot responds to specific words or replies to unregistered message automatically.

registered messages can be controled by admin pages.


## Technical stack
- Flask
- Line Messaging API
- Render(deployment service)
- DeepL API(for translation)
- Dog API(for generating image)
- etc...

## How to deploy this app
### Python version(maybe 3.7.10)
1. create a line bot account and get channel access token and channel secret.
2. create a server on Render
   1. select python as language
   2. set secret environment variables
      - YOUR_CHANNEL_ACCESS_TOKEN
      - YOUR_CHANNEL_SECRET
   3. set build command to `make setup`
   4. set run command to `gunicorn app:app`
3. set webhook url to your server url
   - ex) https://mother-go.onrender.com/callback
4. enable webhook in webhook settings

## Reference

- [LINE Messaging APIの仕様](https://developers.line.biz/ja/reference/messaging-api/)
- [flask deploy on render](https://render.com/docs/deploy-flask)
