這是一個基於 FastAPI 與 LINE Messaging API 開發的輕量化股市情報機器人。它能自動辨識使用者輸入的台股名稱或代號，即時爬取最新新聞，並支援多檔股票同時查詢與產業概念搜尋。

### 🚀 核心功能
多檔股票精準辨識：支援在單一訊息中輸入多個股票名稱（如：台積電、聯發科）或代號（如：2330、2454）。

智能雜訊過濾：內建 Regex 正則表達式，自動過濾日期（如：2026年）等干擾數字，精準鎖定 4-6 碼股票代號。

產業族群追蹤：輸入「伺服器散熱」、「低軌衛星」等關鍵字，系統自動關聯指標股並回傳族群動態。

自動化 CI/CD 部署：完整串接 GitHub 與 Render，實現代碼推播即自動更新部署，維持 24 小時服務。

健全的例外處理：針對 NoneType、KeyError 等邊界條件進行防呆處理，確保伺服器穩定不當機。

🛠️ 技術棧 (Tech Stack)
Backend: Python 3.12, FastAPI, Uvicorn

Scraper: BeautifulSoup4, Requests

API Integration: LINE Messaging API SDK

DevOps: Git, GitHub, Render, python-dotenv

Environment: Venv (Virtual Environment)

### 📂 專案結構 (Project Structure)

```text
.
├── main.py                # 總機：處理 LINE Webhook 入口與訊息組裝
├── message_handler.py     # 大腦：負責意圖識別、雜訊過濾與爬蟲派發
├── stock_relations.json   # 資料庫：儲存股票代號與產業概念對應
├── requirements.txt       # 依賴清單：雲端部署所需的套件清單
├── .env.example           # 環境變數範本
├── .gitignore             # 資安防護：過濾敏感檔案
└── README.md              # 專案說明文件
```

## ⚙️ 本地開發環境設置 (Local Setup)

1. **複製專案並進入資料夾**：
```bash
git clone https://github.com/kiwikiwi710/stock-news-bot.git
cd stock-news-bot
```

2. **建立並啟動虛擬環境 (Windows)**：
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. **安裝必要套件清單**：
```bash
pip install -r requirements.txt
```

4. **啟動測試伺服器**：
```bash
uvicorn main:app --reload
```
☁️ 雲端部署 (Cloud Deployment)
本專案已針對 Render 平台進行優化配置：

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port 10000

Environment Variables: 需在 Render 後台手動新增 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN。
