import json
import os

class StockDictionaryManager:
    def __init__(self, filename: str = 'stock_relations.json'):
        """
        自動取得當前檔案所在目錄的絕對路徑，確保跨平台與不同 IDE 都能正確讀取
        """
        # 取得這支程式的完整絕對路徑與所在資料夾
        # 1. __file__ 代表這支程式(dictionary_manager.py)本身
        # 2. os.path.abspath(__file__) 取得這支程式的完整絕對路徑 (如 C:\...\stock_news_bot\dictionary_manager.py)
        # 3. os.path.dirname() 取得該路徑所在的資料夾 (如 C:\...\stock_news_bot)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 把資料夾路徑跟檔名安全地拼接在一起
        self.filepath = os.path.join(base_dir, filename)
        
        # 載入資料
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """私有方法：處理檔案讀取與錯誤防護"""
        if not os.path.exists(self.filepath):
            print(f"[系統警告] 找不到檔案：{self.filepath}")
            return {"concepts": {}, "stock_info": {}}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("[系統錯誤] JSON 格式解析失敗，請檢查括號或逗號是否正確！")
            return {"concepts": {}, "stock_info": {}}

    def get_stock_name(self, stock_id: str) -> str:
        """
        查詢股票名稱
        範例輸入: "3017" -> 回傳: "奇鋐"
        """
        # 使用 .get() 可以避免找不到 Key 時程式崩潰報錯 (KeyError)
        return self.data.get("stock_info", {}).get(stock_id, {}).get("name", "未知股票")

    def get_related_stocks(self, concept: str) -> dict:
        """
        查詢產業概念的關聯股票
        範例輸入: "伺服器散熱" -> 回傳: {'tw_stocks': ['3017', '3324'], 'us_stocks': ['VRT', 'SMCI']}
        """
        return self.data.get("concepts", {}).get(concept, {})

# ==========================================
# 測試區塊 (只有直接執行此檔案時才會運作)
# ==========================================
if __name__ == "__main__":
    # 實例化管理員
    manager = StockDictionaryManager()
    
    # 測試 1：查股票名稱
    test_id = "6442"
    print(f"代號 {test_id} 的公司名稱是：{manager.get_stock_name(test_id)}")
    
    # 測試 2：查產業關聯
    test_concept = "伺服器散熱"
    related = manager.get_related_stocks(test_concept)
    print(f"【{test_concept}】概念股：")
    print(f"- 台股連動：{related.get('tw_stocks')}")
    print(f"- 美股連動：{related.get('us_stocks')}")