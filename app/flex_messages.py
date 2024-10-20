import datetime

# ヘッダーとフッターの定義
header = {
    "type": "box",
    "layout": "vertical",
    "contents": [
        {
            "type": "text",
            "text": "シフト入力",
            "weight": "bold",
            "size": "xl",
            "align": "center"
        }
    ]
}

footer = {
    "type": "box",
    "layout": "vertical",
    "contents": [
        {
            "type": "button",
            "action": {
                "type": "postback",
                "label": "確定",
                "data": "shift-confirm"
            },
            "style": "primary"
        }
    ]
}

# シフトの種類の定義
shift_types = [
    {"label": "AM", "color": "#8bc34a", "style": "primary"},
    {"label": "PM", "color": "#ff9800", "style": "primary"},
    {"label": "フル", "color": "#f44336", "style": "primary"},
    {"label": "休み", "color": "#9e9e9e", "style": "secondary"}
]

separator = {"type": "separator", "margin": "lg"}

def create_button(date, shift_type):
    """シフト選択用のボタンを生成する"""
    return {
        "type": "button",
        "action": {
            "type": "postback",
            "label": shift_type["label"],
            "data": f"shift={date}={shift_type['label']}"
        },
        "style": shift_type["style"],
        "color": shift_type["color"]
    }

def create_shift_selection_content(date, selected_shift=None):
    """日付とシフト選択内容を含むコンテンツを生成する"""
    contents = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": date.strftime("%m/%d"),
                "size": "md"
            },
            {
                "type": "box",
                "layout": "horizontal",
                "contents": []
            }
        ]
    }

    # シフト選択のボタンを追加
    if selected_shift:
        contents["contents"][1]["contents"].append(create_button(date, selected_shift))
    else:
        for shift_type in shift_types:
            contents["contents"][1]["contents"].append(create_button(date, shift_type))

    return contents

def generate_flex_body(week_dates, data=None):
    """1週間分のシフト選択内容を生成する"""
    body = {"type": "box", "layout": "vertical", "contents": []}

    for date in week_dates:
        selected_shift = None
        if data and date.strftime("%Y-%m-%d") in data:
            selected_shift = next(
                (shift for shift in shift_types if shift["label"] == data[date.strftime("%Y-%m-%d")]), 
                None
            )

        body["contents"].append(create_shift_selection_content(date, selected_shift))
        body["contents"].append(separator)

    return body

def get_shift_selection_flex_message():
    """シフト選択用のFlexメッセージを生成する"""
    today = datetime.datetime.now().date()
    this_week = [today + datetime.timedelta(days=i) for i in range(7)]

    return {
        "type": "bubble",
        "header": header,
        "body": generate_flex_body(this_week),
        "footer": footer
    }

def get_shift_selection_flex_message_with_data(data):
    """事前に選択されたデータを含むシフト選択用のFlexメッセージを生成する"""
    today = datetime.datetime.now().date()
    this_week = [today + datetime.timedelta(days=i) for i in range(7)]

    return {
        "type": "bubble",
        "header": header,
        "body": generate_flex_body(this_week, data),
        "footer": footer
    }
