"""測試 2025-10-07 的訂單"""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WC_URL = os.getenv('WC_URL')
WC_CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
WC_CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')

endpoint = f"{WC_URL.rstrip('/')}/wp-json/wc/v3/orders"
auth = HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET)

# 測試 2025-10-07
test_date = '2025-10-07'

print("=" * 80)
print(f"測試日期: {test_date}")
print("=" * 80)

# 測試各種狀態
statuses = [
    'completed,processing,on-hold',
    'completed,processing,on-hold,wmp-in-transit,wmp-shipped,ry-at-cvs',
    'any'
]

for status in statuses:
    print(f"\n狀態: {status}")
    print("-" * 80)

    params = {
        'after': f'{test_date}T00:00:00',
        'before': f'{test_date}T23:59:59',
        'per_page': 100,
        'status': status
    }

    response = requests.get(endpoint, auth=auth, params=params, timeout=30)

    if response.status_code == 200:
        orders = response.json()
        print(f"訂單數: {len(orders)}")

        if orders:
            total = sum(float(o['total']) for o in orders)
            print(f"總金額: NT$ {total:,.2f}")

            for order in orders:
                print(f"  訂單 #{order['number']}: {order['status']} - NT$ {float(order['total']):,.2f}")
        else:
            print("無訂單")
    else:
        print(f"錯誤: {response.status_code}")

print("\n" + "=" * 80)
