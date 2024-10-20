from fastapi import FastAPI, Request, HTTPException
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent, FlexSendMessage
from app.line_config import handler, line_bot_api
from app.flex_messages import get_shift_selection_flex_message, get_shift_selection_flex_message_with_data

app = FastAPI()

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == "シフト":
        flex_message = get_shift_selection_flex_message()
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="週間シフト", contents=flex_message)
        )
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data == "shift-confirm":
        user_id = event.source.user_id
        if user_id in app.state.shift_data:
            shifts = app.state.shift_data[user_id]

            confirmation_message = "\n".join(
                [f"{date}: {shift}" for date, shift in shifts.items()]
            )

            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text=f"シフトが確定されました:\n{confirmation_message}")
            )

            del app.state.shift_data[user_id]
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="シフト情報が見つかりませんでした。")
            )
    elif data.startswith("shift="):
        shift_info = data.split("=")
        date = shift_info[1]
        shift_type = shift_info[2]

        user_id = event.source.user_id
        if not hasattr(app.state, "shift_data"):
            app.state.shift_data = {}
        if user_id not in app.state.shift_data:
            app.state.shift_data[user_id] = {}

        app.state.shift_data[user_id][date] = shift_type

        # 再生成しない場合はコメントアウト
        # flex_message = get_shift_selection_flex_message_with_data(app.state.shift_data[user_id])
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     FlexSendMessage(alt_text="週間シフト", contents=flex_message)
        # )