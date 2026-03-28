import re
from dictionary_manager import StockDictionaryManager
from news_scraper import YahooFinanceScraper

class StockMessageRouter:
    def __init__(self):
        # 初始化我們的兩大武器
        self.db = StockDictionaryManager()
        self.scraper = YahooFinanceScraper()

    def process_user_input(self, text: str) -> dict:
        """
        解析使用者輸入，判斷意圖並回傳對應的結果字典。
        支援：產業概念、多檔股票名稱、多檔股票代號的混合查詢。
        """
        # 1. 優先處理「產業概念」(Concept)
        for concept, data in self.db.data.get("concepts", {}).items():
            if concept in text:
                return self._handle_concept_search(concept)

        # === 準備一個「不重複」的收集籃 ===
        target_stock_ids = set() 
        stock_info = self.db.data.get("stock_info", {})

        # 2. 檢查是否包含「股票名稱」(動態掃描現有字典，不需要額外的 name_to_id)
        for stock_id, info in stock_info.items():
            stock_name = info.get("name", "")
            if stock_name and stock_name in text:
                target_stock_ids.add(stock_id)

        # 3. 檢查是否包含「股票代號」(利用 Regex 抓出 4~6 碼數字)
        stock_id_matches = re.findall(r'(?<!\d)\d{4,6}(?!\d)', text)
        for stock_id in stock_id_matches:
            if stock_id in stock_info:
                target_stock_ids.add(stock_id)

        # 4. 派發任務：如果收集籃裡有抓到任何股票
        if target_stock_ids:
            multi_results = []
            for stock_id in target_stock_ids:
                single_result = self._handle_single_stock_search(stock_id)
                multi_results.append(single_result)
            
            return {
                "status": "success_multi",
                "results": multi_results
            }
            
        # 5. 終極防線：如果不是概念，也沒有名字，也沒有代號
        return {
            "status": "error",
            "message": "抱歉，目前字典裡沒有找到您提到的股票代號或名稱喔！"
        }
           

    def _handle_single_stock_search(self, stock_id: str) -> dict:
        """處理單一股票查詢"""
        stock_name = self.db.get_stock_name(stock_id)
        print(f"[系統執行] 正在抓取 {stock_name}({stock_id}) 的新聞...")
        news_data = self.scraper.get_tw_stock_news(stock_id)
        
        return {
            "status": "success",
            "type": "single",
            "title": f"【{stock_name} ({stock_id})】最新動態",
            "news": news_data
        }

    def _handle_concept_search(self, concept: str) -> dict:
        """處理產業概念查詢 (台美股連動)"""
        related = self.db.get_related_stocks(concept)
        tw_stocks = related.get("tw_stocks", [])
        us_stocks = related.get("us_stocks", [])

        if not tw_stocks:
            return {"status": "error", "message": f"字典庫中找不到【{concept}】對應的台股。"}

        # 為了 MVP 快速驗證，我們目前先抓清單中的第一檔台股作為代表
        # 未來這裡可以升級成「非同步併發爬蟲」把所有關聯股票都抓齊
        target_id = tw_stocks[0]
        stock_name = self.db.get_stock_name(target_id)
        
        print(f"[系統執行] 正在抓取【{concept}】指標股 {stock_name}({target_id}) 的新聞...")
        news_data = self.scraper.get_tw_stock_news(target_id)

        return {
            "status": "success",
            "type": "concept",
            "title": f"【{concept}】族群動態 (指標股: {stock_name})",
            "us_related": us_stocks, # 把關聯的美股代號傳遞出去，未來可以顯示在 LINE 卡片上
            "news": news_data
        }

# ==========================================
# 測試區塊：模擬 LINE 使用者傳送訊息
# ==========================================
if __name__ == "__main__":
    router = StockMessageRouter()
    
    # 我們準備了四種極端情境來做壓力測試
    test_cases = [
        "幫我查一下伺服器散熱",           # 情境 1：測試「產業概念」(Concept)
        "光聖和台積電",                 # 情境 2：測試「多檔中文名稱」(剛才抓到的 Bug)
        "2026年，幫我比較 2330 和 6442", # 情境 3：測試「多檔數字代號」加雜訊干擾
        "幫我買一杯珍珠奶茶"              # 情境 4：測試「完全無關的幹話」(防呆機制)
    ]
    
    print("="*40)
    print("🚀 系統大腦 (message_handler.py) 壓力測試開始 🚀")
    print("="*40)

    for test_msg in test_cases:
        print(f"\n[模擬使用者輸入] 🗣️ {test_msg}")
        result = router.process_user_input(test_msg)
        
        # 狀態 1：產業概念 (單一回傳結構)
        if result["status"] == "success":
            print(f"✅ [狀態: success] 概念查詢成功！")
            print(f"📊 標題: {result['title']}")
            if result.get("us_related"):
                print(f"🇺🇸 關聯美股: {', '.join(result['us_related'])}")
            for news in result['news'][:2]:
                print(f"  - {news['title']}")
                
        # 狀態 2：單檔/多檔股票 (陣列回傳結構)
        elif result["status"] == "success_multi":
            print(f"✅ [狀態: success_multi] 股票查詢成功！共抓到 {len(result['results'])} 檔股票。")
            for res in result["results"]:
                print(f"\n📊 {res['title']}")
                for news in res['news'][:2]:
                    print(f"  - {news['title']}")
                    
        # 狀態 3：查無此股或防呆攔截
        elif result["status"] == "error":
            print(f"❌ [狀態: error] 系統攔截：{result['message']}")
            
    print("\n" + "="*40)
    print("🎉 所有測試案例執行完畢 🎉")
    print("="*40)