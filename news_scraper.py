import requests
from bs4 import BeautifulSoup

class YahooFinanceScraper:
    def __init__(self):
        # 戴上面具：偽裝成正常的 Windows Chrome 瀏覽器
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_tw_stock_news(self, stock_id: str, max_news: int = 5) -> list:
        """
        輸入股票代號，回傳最新的新聞列表 (包含標題與連結)
        回傳格式: [{"title": "新聞標題", "link": "網址"}, ...]
        """
        # Yahoo 財經的個股新聞網址結構
        url = f"https://tw.stock.yahoo.com/quote/{stock_id}/news"
        
        try:
            # 1. 發送請求 (設定 timeout 避免伺服器無回應時程式卡死)
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status() # 檢查是否發生 404 或 500 錯誤
            
            # 2. 交給 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")
            news_list = []
            
            # 3. 萃取邏輯：找出所有 <a> (超連結) 標籤
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                title = a_tag.text.strip()
                
                # 篩選條件：網址包含 '/news/' 且標題不是空字串或太短的雜訊
                if '/news/' in href and len(title) > 8:
                    
                    # 處理相對路徑網址 (如果網址是 /news/... 開頭，幫它補齊前面)
                    if href.startswith('/'):
                        href = "https://tw.stock.yahoo.com" + href
                        
                    # 避免把同一篇新聞重複加入 (網頁上常有圖片跟標題都連到同一篇)
                    if not any(news['link'] == href for news in news_list):
                        news_list.append({
                            "title": title,
                            "link": href
                        })
                        
                    # 如果抓夠了我們設定的數量 (預設 5 篇)，就提早結束迴圈
                    if len(news_list) >= max_news:
                        break
                        
            return news_list
            
        except Exception as e:
            # 錯誤處理：如果網路斷線或被擋，回傳空陣列，不要讓整個系統崩潰
            print(f"[系統警告] 抓取 {stock_id} 新聞時發生異常: {e}")
            return []

# ==========================================
# 測試區塊 (只有直接執行此檔案時才會運作)
# ==========================================
if __name__ == "__main__":
    scraper = YahooFinanceScraper()
    
    # 測試抓取奇鋐 (3017) 的新聞
    test_id = "3017"
    print(f"正在抓取 {test_id} 的最新新聞...\n")
    
    results = scraper.get_tw_stock_news(test_id)
    
    if results:
        for idx, news in enumerate(results, 1):
            print(f"{idx}. {news['title']}")
            print(f"   連結: {news['link']}\n")
    else:
        print("沒有抓到任何新聞，請檢查網路狀態或網址結構。")