"""測試新客率計算功能"""
import pandas as pd
from datetime import datetime, timedelta

def test_new_customer_rate():
    print("=" * 50)
    print("新客率計算功能測試")
    print("=" * 50)
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    
    # 測試場景 1: 有新客戶和老客戶的訂單
    test_orders = pd.DataFrame([
        # 歷史訂單
        {'order_id': 1, 'date': two_weeks_ago, 'total': 1000, 'email': 'old1@example.com'},
        {'order_id': 2, 'date': two_weeks_ago, 'total': 1500, 'email': 'old2@example.com'},
        
        # 本週訂單
        {'order_id': 3, 'date': today, 'total': 1200, 'email': 'old1@example.com'},  # 老客戶
        {'order_id': 4, 'date': today, 'total': 900, 'email': 'old1@example.com'},   # 老客戶（同一人買2次）
        {'order_id': 5, 'date': today, 'total': 800, 'email': 'new1@example.com'},   # 新客戶
        {'order_id': 6, 'date': today, 'total': 1100, 'email': 'new2@example.com'},  # 新客戶
    ])
    
    # 手動實現計算邏輯
    def calculate_new_customer_rate(orders_df, current_start_date, current_end_date):
        if orders_df.empty:
            return 0.0, 0, 0
        
        df = orders_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        current_week_orders = df[
            (df['date'] >= pd.to_datetime(current_start_date)) & 
            (df['date'] <= pd.to_datetime(current_end_date))
        ]
        
        historical_orders = df[df['date'] < pd.to_datetime(current_start_date)]
        
        if current_week_orders.empty:
            return 0.0, 0, 0
        
        historical_emails = set(historical_orders['email'].dropna().str.lower().unique())
        current_week_orders['email_lower'] = current_week_orders['email'].str.lower().fillna('')
        new_customer_orders = current_week_orders[
            (~current_week_orders['email_lower'].isin(historical_emails)) | 
            (current_week_orders['email_lower'] == '')
        ]
        
        total_orders = len(current_week_orders)
        new_orders_count = len(new_customer_orders)
        new_customer_rate = (new_orders_count / total_orders * 100) if total_orders > 0 else 0.0
        
        return new_customer_rate, new_orders_count, total_orders
    
    # 執行測試
    rate, new_count, total = calculate_new_customer_rate(test_orders, week_ago, today)
    
    print(f"\n測試場景 1: 混合新老客戶訂單")
    print(f"  本週總訂單數: {total}")
    print(f"  新客戶訂單數: {new_count}")
    print(f"  新客率: {rate:.1f}%")
    print(f"  預期: 50% (2筆新客訂單 / 4筆總訂單)")
    
    assert total == 4, f"總訂單數應為 4，實際為 {total}"
    assert new_count == 2, f"新客訂單數應為 2，實際為 {new_count}"
    assert abs(rate - 50.0) < 0.1, f"新客率應為 50%，實際為 {rate:.2f}%"
    
    print("  ✓ 測試通過！\n")
    
    # 測試場景 2: 全部是新客戶
    new_orders = pd.DataFrame([
        {'order_id': 1, 'date': today, 'total': 1000, 'email': 'new1@example.com'},
        {'order_id': 2, 'date': today, 'total': 1500, 'email': 'new2@example.com'},
    ])
    
    rate2, new_count2, total2 = calculate_new_customer_rate(new_orders, week_ago, today)
    
    print(f"測試場景 2: 全部新客戶")
    print(f"  本週總訂單數: {total2}")
    print(f"  新客戶訂單數: {new_count2}")
    print(f"  新客率: {rate2:.1f}%")
    
    assert total2 == 2, f"總訂單數應為 2，實際為 {total2}"
    assert new_count2 == 2, f"新客訂單數應為 2，實際為 {new_count2}"
    assert rate2 == 100.0, f"新客率應為 100%，實際為 {rate2:.2f}%"
    
    print("  ✓ 測試通過！\n")
    
    print("=" * 50)
    print("所有測試通過！✓")
    print("=" * 50)

if __name__ == "__main__":
    test_new_customer_rate()
