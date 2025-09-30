#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta API 調試工具
專門用來診斷廣告費為零的問題
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd

def debug_meta_api(access_token, account_id, days_back=7):
    """
    調試 Meta API 廣告數據獲取

    Args:
        access_token: Meta API 存取權杖
        account_id: 廣告帳號 ID
        days_back: 往前查詢天數
    """

    print("🔍 Meta API 廣告費調試工具")
    print("=" * 60)

    # 確保帳號ID格式正確
    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"

    print(f"📊 廣告帳號: {account_id}")

    # 設定查詢日期範圍
    end_date = datetime.now().date() - timedelta(days=1)  # 避免查詢今天
    start_date = end_date - timedelta(days=days_back)

    print(f"📅 查詢期間: {start_date} 至 {end_date}")
    print()

    # API 設定
    url = f"https://graph.facebook.com/v23.0/{account_id}/insights"

    # 正確的時間範圍格式
    time_range = json.dumps({
        'since': start_date.strftime('%Y-%m-%d'),
        'until': end_date.strftime('%Y-%m-%d')
    })

    params = {
        'access_token': access_token,
        'fields': 'spend,impressions,clicks,reach,date_start,date_stop,account_name',
        'time_range': time_range,
        'level': 'account',
        'time_increment': 1,
        'limit': 100
    }

    print("🚀 發送 API 請求...")
    print(f"URL: {url}")
    print(f"參數: {json.dumps({k: v for k, v in params.items() if k != 'access_token'}, indent=2)}")
    print()

    try:
        response = requests.get(url, params=params, timeout=30)

        print(f"📡 HTTP 狀態碼: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("✅ API 請求成功！")
            print()

            # 顯示完整響應結構
            print("📋 完整 API 響應:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()

            # 分析數據
            insights_data = data.get('data', [])
            print(f"📊 共獲取 {len(insights_data)} 筆數據")

            if insights_data:
                print("\n📈 每日數據分析:")
                print("-" * 40)

                total_spend = 0
                zero_days = 0

                for i, item in enumerate(insights_data):
                    date_str = item.get('date_start', 'Unknown')
                    spend = float(item.get('spend', 0))
                    impressions = int(item.get('impressions', 0))
                    clicks = int(item.get('clicks', 0))

                    total_spend += spend
                    if spend == 0:
                        zero_days += 1

                    status = "⚠️ 零支出" if spend == 0 else "✅ 有支出"

                    print(f"{date_str}: ${spend:8.2f} | 曝光: {impressions:6,} | 點擊: {clicks:4,} | {status}")

                print("-" * 40)
                print(f"📊 統計摘要:")
                print(f"   總廣告費: ${total_spend:.2f}")
                print(f"   零支出天數: {zero_days}/{len(insights_data)} 天")
                print(f"   平均每日支出: ${total_spend/len(insights_data):.2f}")

                if zero_days > 0:
                    print(f"\n⚠️ 發現 {zero_days} 天廣告費為零")
                    print("可能原因:")
                    print("1. 該期間確實沒有投放廣告")
                    print("2. 廣告被暫停或預算用完")
                    print("3. API 數據延遲或同步問題")
                    print("4. 查詢的時間範圍包含未來日期")

            else:
                print("⚠️ 沒有獲取到任何廣告數據")
                print("可能原因:")
                print("1. 帳號 ID 錯誤")
                print("2. 查詢期間沒有廣告活動")
                print("3. API 權限不足")
                print("4. 帳號狀態異常")

        else:
            print(f"❌ API 請求失敗")
            print(f"狀態碼: {response.status_code}")
            print(f"響應內容: {response.text}")

            # 嘗試解析錯誤訊息
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error = error_data['error']
                    print(f"\n錯誤詳情:")
                    print(f"- 錯誤代碼: {error.get('code', 'Unknown')}")
                    print(f"- 錯誤訊息: {error.get('message', 'Unknown')}")
                    print(f"- 錯誤類型: {error.get('type', 'Unknown')}")
            except:
                pass

    except Exception as e:
        print(f"❌ 發生異常: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

def test_account_access(access_token, account_id):
    """測試帳號存取權限"""
    print("\n🔐 測試帳號存取權限...")

    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"

    url = f"https://graph.facebook.com/v23.0/{account_id}"
    params = {
        'access_token': access_token,
        'fields': 'name,account_status,currency,amount_spent,balance'
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ 帳號存取正常")
            print(f"帳號名稱: {data.get('name', 'N/A')}")
            print(f"帳號狀態: {data.get('account_status', 'N/A')}")
            print(f"幣別: {data.get('currency', 'N/A')}")
            print(f"累計消費: ${data.get('amount_spent', 0)}")
            return True
        else:
            print(f"❌ 帳號存取失敗: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 測試帳號存取時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    # 請在這裡填入你的設定
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
    ACCOUNT_ID = "YOUR_ACCOUNT_ID_HERE"  # 可以包含或不包含 "act_" 前綴

    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE" or ACCOUNT_ID == "YOUR_ACCOUNT_ID_HERE":
        print("❌ 請先設定你的 ACCESS_TOKEN 和 ACCOUNT_ID")
        print("在檔案頂部修改這兩個變數")
    else:
        # 先測試帳號存取
        if test_account_access(ACCESS_TOKEN, ACCOUNT_ID):
            # 再進行詳細的廣告數據調試
            debug_meta_api(ACCESS_TOKEN, ACCOUNT_ID, days_back=10)
        else:
            print("⚠️ 帳號存取測試失敗，請檢查 TOKEN 和帳號 ID")