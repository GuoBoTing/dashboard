"""測試 WooCommerce 訂單抓取（包含自訂狀態）"""
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 設定
WC_URL = os.getenv('WC_URL')
WC_CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
WC_CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')

# 測試日期範圍：最近 7 天
from datetime import timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

print("=" * 80)
print("WooCommerce 訂單狀態測試")
print("=" * 80)
print(f"\n測試日期範圍: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print(f"商店 URL: {WC_URL}\n")

# 測試不同的狀態組合
test_cases = [
    {
        'name': '原始狀態（不含自訂）',
        'status': 'completed,processing,on-hold'
    },
    {
        'name': '新增自訂狀態',
        'status': 'completed,processing,on-hold,wmp-in-transit,wmp-shipped,ry-at-cvs'
    },
    {
        'name': '所有狀態',
        'status': 'any'
    }
]

endpoint = f"{WC_URL.rstrip('/')}/wp-json/wc/v3/orders"
auth = HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET)

for test in test_cases:
    print(f"\n{'─' * 80}")
    print(f"測試: {test['name']}")
    print(f"狀態: {test['status']}")
    print('─' * 80)

    params = {
        'after': start_date.strftime('%Y-%m-%dT00:00:00'),
        'before': end_date.strftime('%Y-%m-%dT23:59:59'),
        'per_page': 100,
        'status': test['status']
    }

    try:
        response = requests.get(endpoint, auth=auth, params=params, timeout=30)

        if response.status_code == 200:
            orders = response.json()
            print(f"✅ 成功抓取 {len(orders)} 筆訂單")

            if orders:
                total_revenue = sum(float(order['total']) for order in orders)
                print(f"總營收: NT$ {total_revenue:,.2f}")

                # 統計各狀態訂單數
                status_count = {}
                for order in orders:
                    status = order['status']
                    status_count[status] = status_count.get(status, 0) + 1

                print(f"\n訂單狀態分佈:")
                for status, count in sorted(status_count.items()):
                    status_orders = [o for o in orders if o['status'] == status]
                    status_revenue = sum(float(o['total']) for o in status_orders)
                    print(f"  - {status}: {count} 筆, NT$ {status_revenue:,.2f}")
            else:
                print("⚠️ 該日期無訂單")
        else:
            print(f"❌ API 錯誤: {response.status_code}")
            print(f"   訊息: {response.text[:200]}")

    except Exception as e:
        print(f"❌ 請求失敗: {str(e)}")

print(f"\n{'=' * 80}")
print("測試完成")
print("=" * 80)
