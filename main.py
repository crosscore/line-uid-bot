from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = FastAPI()

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

if CHANNEL_ACCESS_TOKEN is None or CHANNEL_SECRET is None:
    raise ValueError("Environment variables 'CHANNEL_ACCESS_TOKEN' and 'CHANNEL_SECRET' must be set.")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")

    body = await request.body()
    body_str = body.decode("utf-8")

    print("Request body: " + body_str)

    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event):
    user_id = event.source.user_id

    print(f"Received message from user: {user_id}")
    await line_bot_api.push_message(to=user_id, messages=TextSendMessage(text=f"Your UID is {user_id}"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)