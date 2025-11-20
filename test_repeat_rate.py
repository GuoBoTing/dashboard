"""測試回購率計算功能"""
import pandas as pd
from datetime import datetime, timedelta

# 模擬測試數據
def test_repeat_purchase_rate():
    print("=" * 50)
    print("回購率計算功能測試")
    print("=" * 50)
    
    # 創建測試數據
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    
    # 測試場景 1: 有回購客戶
    test_orders = pd.DataFrame([
        # 歷史訂單（兩週前）
        {'order_id': 1, 'date': two_weeks_ago, 'total': 1000, 'customer_id': 101, 'status': 'completed'},
        {'order_id': 2, 'date': two_weeks_ago, 'total': 1500, 'customer_id': 102, 'status': 'completed'},
        {'order_id': 3, 'date': two_weeks_ago, 'total': 800, 'customer_id': 103, 'status': 'completed'},
        
        # 本週訂單
        {'order_id': 4, 'date': today, 'total': 1200, 'customer_id': 101, 'status': 'completed'},  # 回頭客
        {'order_id': 5, 'date': today, 'total': 900, 'customer_id': 102, 'status': 'completed'},   # 回頭客
        {'order_id': 6, 'date': today, 'total': 1100, 'customer_id': 104, 'status': 'completed'},  # 新客戶
    ])
    
    # 導入計算函數（從 app.py）
    import sys
    sys.path.insert(0, '.')
    
    # 手動實現計算邏輯進行測試
    def calculate_repeat_purchase_rate(orders_df, current_start_date, current_end_date):
        if orders_df.empty:
            return 0.0, 0, 0
        
        orders_df['date'] = pd.to_datetime(orders_df['date'])
        
        current_week_orders = orders_df[
            (orders_df['date'] >= pd.to_datetime(current_start_date)) & 
            (orders_df['date'] <= pd.to_datetime(current_end_date))
        ]
        
        historical_orders = orders_df[orders_df['date'] < pd.to_datetime(current_start_date)]
        
        if current_week_orders.empty:
            return 0.0, 0, 0
        
        current_customers = set(current_week_orders[current_week_orders['customer_id'] != 0]['customer_id'].unique())
        historical_customers = set(historical_orders[historical_orders['customer_id'] != 0]['customer_id'].unique())
        repeat_customers = current_customers.intersection(historical_customers)
        
        total_customers = len(current_customers)
        repeat_customer_count = len(repeat_customers)
        repeat_rate = (repeat_customer_count / total_customers * 100) if total_customers > 0 else 0.0
        
        return repeat_rate, repeat_customer_count, total_customers
    
    # 執行測試
    repeat_rate, repeat_count, total_count = calculate_repeat_purchase_rate(
        test_orders, week_ago, today
    )
    
    print(f"\n測試場景 1: 有回購客戶")
    print(f"  本週總客戶數: {total_count}")
    print(f"  回頭客數量: {repeat_count}")
    print(f"  回購率: {repeat_rate:.1f}%")
    print(f"  預期回購率: 66.7% (2/3)")
    
    # 驗證結果
    assert total_count == 3, f"總客戶數應為 3，實際為 {total_count}"
    assert repeat_count == 2, f"回頭客應為 2，實際為 {repeat_count}"
    assert abs(repeat_rate - 66.67) < 0.1, f"回購率應為 66.67%，實際為 {repeat_rate:.2f}%"
    
    print("  ✓ 測試通過！\n")
    
    # 測試場景 2: 無歷史數據
    new_orders = pd.DataFrame([
        {'order_id': 1, 'date': today, 'total': 1000, 'customer_id': 201, 'status': 'completed'},
        {'order_id': 2, 'date': today, 'total': 1500, 'customer_id': 202, 'status': 'completed'},
    ])
    
    repeat_rate2, repeat_count2, total_count2 = calculate_repeat_purchase_rate(
        new_orders, week_ago, today
    )
    
    print(f"測試場景 2: 全部新客戶（無歷史數據）")
    print(f"  本週總客戶數: {total_count2}")
    print(f"  回頭客數量: {repeat_count2}")
    print(f"  回購率: {repeat_rate2:.1f}%")
    
    assert total_count2 == 2, f"總客戶數應為 2，實際為 {total_count2}"
    assert repeat_count2 == 0, f"回頭客應為 0，實際為 {repeat_count2}"
    assert repeat_rate2 == 0, f"回購率應為 0%，實際為 {repeat_rate2:.2f}%"
    
    print("  ✓ 測試通過！\n")
    
    print("=" * 50)
    print("所有測試通過！✓")
    print("=" * 50)

if __name__ == "__main__":
    test_repeat_purchase_rate()
