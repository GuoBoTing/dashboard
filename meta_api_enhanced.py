# meta_api_enhanced.py
import requests
import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class MetaAdsAPI:
    """增強版 Meta Ads API 客戶端（含自動 Token 刷新）"""
    
    def __init__(self, app_id: str, app_secret: str, account_id: str, long_lived_token: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.account_id = account_id if account_id.startswith('act_') else f"act_{account_id}"
        self.base_url = "https://graph.facebook.com/v21.0"
        self.current_token = long_lived_token
        
        # 從 session state 恢復 token 信息
        if 'meta_token_info' in st.session_state:
            token_info = st.session_state.meta_token_info
            self.current_token = token_info.get('access_token', self.current_token)
    
    def _save_token_info(self, token_info: dict):
        """保存 token 信息到 session state"""
        st.session_state.meta_token_info = token_info
        self.current_token = token_info['access_token']
    
    def _is_token_expired(self) -> bool:
        """檢查 token 是否即將過期"""
        if 'meta_token_info' not in st.session_state:
            return True
        
        token_info = st.session_state.meta_token_info
        if 'expires_at' not in token_info:
            return True
        
        try:
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            # 如果在 7 天內過期，視為需要刷新
            return expires_at < datetime.now() + timedelta(days=7)
        except:
            return True
    
    def refresh_long_lived_token(self, current_token: str = None) -> dict:
        """刷新長期 Token"""
        token_to_refresh = current_token or self.current_token
        
        if not token_to_refresh:
            raise Exception("沒有可用的 token 進行刷新")
        
        url = f"{self.base_url}/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': token_to_refresh
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            expires_in = data.get('expires_in', 5183944)  # 默認 60 天
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            token_info = {
                'access_token': data['access_token'],
                'expires_in': expires_in,
                'expires_at': expires_at.isoformat(),
                'token_type': data.get('token_type', 'bearer'),
                'refreshed_at': datetime.now().isoformat()
            }
            
            self._save_token_info(token_info)
            
            st.success(f"Token 已成功刷新，有效期至：{expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return token_info
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Token 刷新失敗: {str(e)}"
            st.error(error_msg)
            raise Exception(error_msg)
    
    def _validate_and_refresh_token(self) -> str:
        """驗證並刷新 token"""
        # 檢查是否需要刷新
        if self._is_token_expired():
            st.info("檢測到 Token 即將過期，正在自動刷新...")
            try:
                self.refresh_long_lived_token()
            except Exception as e:
                st.error(f"自動刷新 Token 失敗: {str(e)}")
                raise
        
        return self.current_token
    
    def _make_api_request(self, endpoint: str, params: dict = None, method: str = 'GET') -> dict:
        """發送 API 請求（含錯誤處理和自動重試）"""
        if params is None:
            params = {}
        
        # 確保 token 有效
        try:
            token = self._validate_and_refresh_token()
            params['access_token'] = token
        except Exception as e:
            raise Exception(f"Token 驗證失敗: {str(e)}")
        
        url = f"{self.base_url}/{endpoint}"
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=30)
                else:
                    response = requests.post(url, data=params, timeout=30)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                response_text = getattr(e.response, 'text', '') if hasattr(e, 'response') else ''
                
                # 檢查是否為 token 相關錯誤
                if hasattr(e, 'response') and e.response and e.response.status_code in [401, 403]:
                    try:
                        error_data = e.response.json()
                        error_code = error_data.get('error', {}).get('code')
                        
                        # Token 無效或過期
                        if error_code in [190, 102, 463]:
                            if attempt < max_retries - 1:
                                st.warning("Token 無效，嘗試刷新...")
                                try:
                                    self.refresh_long_lived_token()
                                    params['access_token'] = self.current_token
                                    continue  # 重試
                                except:
                                    pass
                        
                    except json.JSONDecodeError:
                        pass
                
                # 其他錯誤或最後一次重試失敗
                if attempt == max_retries - 1:
                    error_msg = f"API 請求失敗: {str(e)}"
                    if response_text:
                        error_msg += f"\n響應內容: {response_text}"
                    raise Exception(error_msg)
                
                # 短暫延遲後重試
                import time
                time.sleep(1)
    
    def get_ads_insights(self, start_date: datetime, end_date: datetime) -> dict:
        """獲取廣告洞察數據"""
        endpoint = f"{self.account_id}/insights"
        params = {
            'fields': 'spend,impressions,clicks,reach,frequency,cpm,cpc,ctr',
            'time_range': json.dumps({
                'since': start_date.strftime('%Y-%m-%d'),
                'until': end_date.strftime('%Y-%m-%d')
            }),
            'level': 'account',
            'time_increment': 1
        }
        
        return self._make_api_request(endpoint, params)
    
    def get_account_info(self) -> dict:
        """獲取帳號信息"""
        endpoint = f"{self.account_id}"
        params = {'fields': 'name,account_status,amount_spent,balance,currency'}
        
        return self._make_api_request(endpoint, params)
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            endpoint = f"{self.account_id}"
            params = {'fields': 'name'}
            result = self._make_api_request(endpoint, params)
            return 'name' in result
        except:
            return False

def get_enhanced_meta_ads_data(config: dict, start_date: datetime, end_date: datetime):
    """使用增強版 Meta API 獲取數據"""
    try:
        # 初始化 API 客戶端
        api_client = MetaAdsAPI(
            app_id=config['app_id'],
            app_secret=config['app_secret'],
            account_id=config['account_id'],
            long_lived_token=config.get('long_lived_token')
        )
        
        # 測試連接
        if not api_client.test_connection():
            st.error("Meta API 連接測試失敗")
            return pd.DataFrame()
        
        with st.spinner("正在獲取 Meta 廣告數據..."):
            # 獲取廣告數據
            insights_data = api_client.get_ads_insights(start_date, end_date)
            
            # 處理數據
            processed_data = []
            for item in insights_data.get('data', []):
                processed_data.append({
                    'date': pd.to_datetime(item['date_start']).date(),
                    'spend': float(item.get('spend', 0)),
                    'impressions': int(item.get('impressions', 0)),
                    'clicks': int(item.get('clicks', 0)),
                    'reach': int(item.get('reach', 0)),
                    'ctr': float(item.get('ctr', 0)),
                    'cpm': float(item.get('cpm', 0)),
                    'cpc': float(item.get('cpc', 0))
                })
            
            df = pd.DataFrame(processed_data)
            
            if not df.empty:
                st.success(f"成功獲取 {len(processed_data)} 筆 Meta 廣告數據")
            else:
                st.info("指定期間內沒有廣告數據")
            
            return df
            
    except Exception as e:
        st.error(f"Meta 廣告數據獲取失敗: {str(e)}")
        return pd.DataFrame()

def show_token_management():
    """顯示 Token 管理界面"""
    # 為了避免循環導入，直接在這裡實現簡化版本
    st.subheader("Meta Token 管理")
    
    # 顯示當前 token 狀態
    if 'meta_token_info' in st.session_state:
        token_info = st.session_state.meta_token_info
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**當前 Token 狀態**")
            if 'expires_at' in token_info:
                expires_at = datetime.fromisoformat(token_info['expires_at'])
                days_left = (expires_at - datetime.now()).days
                
                if days_left > 7:
                    st.success(f"Token 有效，剩餘 {days_left} 天")
                elif days_left > 0:
                    st.warning(f"Token 將在 {days_left} 天後過期")
                else:
                    st.error("Token 已過期")
                
                st.caption(f"到期時間: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            if st.button("手動刷新 Token"):
                try:
                    # 這裡需要獲取配置，但為了避免循環導入，簡化處理
                    st.info("請使用下方的初始化功能重新生成 Token")
                except Exception as e:
                    st.error(f"刷新失敗: {str(e)}")
    else:
        st.info("尚未設定 Token 信息")
    
    # 初始化長期 Token
    with st.expander("初始化長期 Token"):
        st.info("首次使用時，請使用短期 Token 生成長期 Token")
        short_token = st.text_input("短期 Access Token", type="password", key="short_token_input")
        
        if st.button("生成長期 Token") and short_token:
            try:
                # 獲取 Meta 配置
                if hasattr(st, 'secrets') and 'meta' in st.secrets:
                    app_id = st.secrets.meta.app_id
                    app_secret = st.secrets.meta.app_secret
                    account_id = st.secrets.meta.account_id
                    
                    api_client = MetaAdsAPI(
                        app_id=app_id,
                        app_secret=app_secret,
                        account_id=account_id
                    )
                    token_info = api_client.refresh_long_lived_token(short_token)
                    st.success("長期 Token 生成成功！")
                    st.json(token_info)
                else:
                    st.error("無法獲取 Meta API 配置")
            except Exception as e:
                st.error(f"生成失敗: {str(e)}")