import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 匯入我們自己寫的系統大腦
from message_handler import StockMessageRouter

# 1. 載入 .env 保險箱裡的金鑰
load_dotenv()
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if not channel_secret or not channel_access_token:
    print("[系統崩潰] 找不到 LINE 金鑰，請檢查 .env 檔案！")
    exit(1)

# 2. 初始化 FastAPI 伺服器與 LINE 模組
app = FastAPI()
configuration = Configuration(access_token=channel_access_token)
parser = WebhookParser(channel_secret)
router = StockMessageRouter() # 實例化我們的大腦

# 3. 建立接收 LINE 訊息的路由 (Endpoint)
@app.post("/callback")
async def handle_callback(request: Request):
    # 取得 LINE 的安全簽名並讀取訊息內容
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_decode = body.decode('utf-8')

    # 驗證訊息真的來自 LINE 官方 (防駭客偽造)
    try:
        events = parser.parse(body_decode, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature. 請確認 Channel Secret 是否正確。")

    # 處理每一筆收到的事件
    for event in events:
        # 我們目前只處理「文字訊息」，圖片或貼圖先忽略
        if not isinstance(event, MessageEvent) or not isinstance(event.message, TextMessageContent):
            continue

        # 擷取使用者輸入的文字
        user_text = event.message.text
        print(f"[收到 LINE 訊息] {user_text}")
        
       # 交給大腦解析並抓新聞
        result = router.process_user_input(user_text)
        
        # === 開始將抓取結果組裝成文字回覆 ===
        if result["status"] == "success":
            # 處理單一產業概念的格式
            reply_text = f"📊 {result['title']}\n"
            if result.get("us_related"):
                reply_text += f"🇺🇸 關聯美股: {', '.join(result['us_related'])}\n"
            reply_text += "-" * 15 + "\n"
            for idx, news in enumerate(result['news'][:3], 1):
                reply_text += f"{idx}. {news['title']}\n{news['link']}\n\n"
                
        elif result["status"] == "success_multi":
            # 處理多檔股票的格式 (走訪 results 陣列)
            reply_text = ""
            for res in result["results"]:
                reply_text += f"📊 {res['title']}\n"
                if res.get("us_related"):
                    reply_text += f"🇺🇸 關聯美股: {', '.join(res['us_related'])}\n"
                reply_text += "-" * 15 + "\n"
                # 多檔股票時，每檔取前 2 篇避免版面太長
                for idx, news in enumerate(res['news'][:2], 1): 
                    reply_text += f"{idx}. {news['title']}\n{news['link']}\n\n"
                reply_text += "================\n"
                
        else:
            # 處理錯誤訊息，使用 .get() 加上預設值，避免再度發生 KeyError
            reply_text = result.get("message", "系統發生未知錯誤，請稍後再試。")
            
        # ==================================

        # 呼叫 LINE API 把文字傳送回使用者的手機
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text.strip())]
                )
            )

    return "OK"