#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版 Meta API 測試程式
適合初學者使用
"""

import requests
import json
from datetime import datetime, timedelta

def test_meta_api():
    """簡單的 Meta API 測試"""
    
    print("🚀 Meta Ads API 測試開始")
    print("=" * 50)
    
    # ⚠️ 請在這裡填入你的 Access Token
    ACCESS_TOKEN = "EAAgilHDit9sBPciQ7txcmlGKBwHrFziWfE18L8QX8xPunp2jnUZBcAWx8G2ZCZCJdHXZCRRZC4ujRUPyDmsyTrSIWoRXZBn3Q7dyZBPhANbj9Cs5TvFuXG66vFYQhdBZC0ZBJQeflranPj2A6kuVwrdvADymhFMDTaRaTVOzxpgEQMQfdZATelDXItTi1Gaq9Cdm36Pi6GaEKJ"
    
    # 檢查是否有設定 Token
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("❌ 請先設定你的 Access Token！")
        print("請將上面的 YOUR_ACCESS_TOKEN_HERE 替換為你的實際 Token")
        print("Token 格式類似：EAAxxxxxxxxxxxxxxxxxxxxxxx")
        return
    
    # API 基本設定
    API_VERSION = "v21.0"
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
    
    print(f"📡 使用 API 版本: {API_VERSION}")
    print()
    
    # 測試 1: 基本連接測試
    print("🔍 測試 1: API 連接測試")
    try:
        url = f"{BASE_URL}/me"
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,name'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 連接成功！")
            print(f"   用戶 ID: {data.get('id', 'N/A')}")
            print(f"   用戶名稱: {data.get('name', 'N/A')}")
        else:
            print(f"❌ 連接失敗 - 狀態碼: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 連接錯誤: {str(e)}")
        return
    
    print()
    
    # 測試 2: 獲取廣告帳號
    print("🏢 測試 2: 獲取廣告帳號")
    try:
        url = f"{BASE_URL}/me/adaccounts"
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,name,account_id,currency,account_status',
            'limit': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            
            print(f"✅ 找到 {len(accounts)} 個廣告帳號")
            
            if accounts:
                for i, account in enumerate(accounts, 1):
                    print(f"   📊 帳號 {i}:")
                    print(f"      ID: {account.get('id', 'N/A')}")
                    print(f"      名稱: {account.get('name', 'N/A')}")
                    print(f"      幣別: {account.get('currency', 'N/A')}")
                    print(f"      狀態: {account.get('account_status', 'N/A')}")
                    print()
                
                # 儲存第一個帳號 ID 供後續測試使用
                first_account_id = accounts[0]['id']
                
            else:
                print("   ⚠️ 沒有找到廣告帳號")
                print("   可能原因：")
                print("   - 帳號沒有廣告權限")
                print("   - Token 權限不足")
                print("   - 還沒有建立廣告帳號")
                return
                
        else:
            print(f"❌ 獲取帳號失敗 - 狀態碼: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 獲取帳號錯誤: {str(e)}")
        return
    
    print()
    
    # 測試 3: 獲取廣告活動（如果有帳號的話）
    print("📈 測試 3: 獲取廣告活動")
    try:
        url = f"{BASE_URL}/{first_account_id}/campaigns"
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,name,objective,status',
            'limit': 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            
            print(f"✅ 找到 {len(campaigns)} 個廣告活動")
            
            if campaigns:
                for i, campaign in enumerate(campaigns, 1):
                    print(f"   🎯 活動 {i}:")
                    print(f"      ID: {campaign.get('id', 'N/A')}")
                    print(f"      名稱: {campaign.get('name', 'N/A')}")
                    print(f"      目標: {campaign.get('objective', 'N/A')}")
                    print(f"      狀態: {campaign.get('status', 'N/A')}")
                    print()
            else:
                print("   ℹ️ 目前沒有廣告活動")
                print("   這是正常的，如果你還沒有投放廣告")
                
        else:
            print(f"❌ 獲取活動失敗 - 狀態碼: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 獲取活動錯誤: {str(e)}")
    
    print()
    
    # 測試完成
    print("🎉 測試完成！")
    print("=" * 50)
    print("📋 測試結果摘要：")
    print("✅ 如果看到帳號資訊，表示 API 連接成功")
    print("✅ 如果看到廣告活動，表示你可以獲取廣告數據")
    print("ℹ️ 沒有廣告活動也是正常的（如果你還沒投放廣告）")
    print()
    print("🔧 下一步：")
    print("1. 確保所有測試都成功")
    print("2. 記錄你的廣告帳號 ID")
    print("3. 開始整合到 Streamlit Dashboard 中")

if __name__ == "__main__":
    test_meta_api()