# config.py - 配置管理
import streamlit as st
import os
from typing import Optional, Tuple, Dict, Any

class Config:
    """安全配置管理類"""
    
    def __init__(self):
        """初始化配置"""
        self.woocommerce_config = self._load_woocommerce_config()
        self.meta_config = self._load_meta_config()
    
    def _load_woocommerce_config(self) -> Dict[str, str]:
        """載入 WooCommerce 配置"""
        try:
            # 優先從 Streamlit secrets 讀取
            if hasattr(st, 'secrets') and 'woocommerce' in st.secrets:
                return {
                    'url': st.secrets.woocommerce.url,
                    'consumer_key': st.secrets.woocommerce.consumer_key,
                    'consumer_secret': st.secrets.woocommerce.consumer_secret
                }
        except Exception:
            pass
        
        # 備用：從環境變數讀取
        return {
            'url': os.getenv('WC_URL', ''),
            'consumer_key': os.getenv('WC_CONSUMER_KEY', ''),
            'consumer_secret': os.getenv('WC_CONSUMER_SECRET', '')
        }
    
    def _load_meta_config(self) -> Dict[str, str]:
        """載入 Meta 配置"""
        try:
            # 優先從 Streamlit secrets 讀取
            if hasattr(st, 'secrets') and 'meta' in st.secrets:
                return {
                    'app_id': st.secrets.meta.app_id,
                    'app_secret': st.secrets.meta.app_secret,
                    'account_id': st.secrets.meta.account_id,
                    'long_lived_token': st.secrets.meta.get('long_lived_token', ''),
                    'oauth_redirect_uri': st.secrets.meta.get('oauth_redirect_uri', 'http://localhost:8501')
                }
        except Exception:
            pass

        # 備用：從環境變數讀取
        return {
            'app_id': os.getenv('META_APP_ID', ''),
            'app_secret': os.getenv('META_APP_SECRET', ''),
            'account_id': os.getenv('META_ACCOUNT_ID', ''),
            'long_lived_token': os.getenv('META_LONG_LIVED_TOKEN', ''),
            'oauth_redirect_uri': os.getenv('META_OAUTH_REDIRECT_URI', 'http://localhost:8501')
        }
    
    def is_configured(self) -> Tuple[bool, bool]:
        """
        檢查 API 是否已配置
        
        Returns:
            Tuple of (woocommerce_configured, meta_configured)
        """
        woocommerce_configured = (
            self.woocommerce_config and
            self.woocommerce_config.get('url') and
            self.woocommerce_config.get('consumer_key') and
            self.woocommerce_config.get('consumer_secret')
        )
        
        meta_configured = (
            self.meta_config and
            self.meta_config.get('app_id') and
            self.meta_config.get('app_secret') and
            self.meta_config.get('account_id')
        )
        
        return woocommerce_configured, meta_configured
    
    def get_woocommerce_config(self) -> Dict[str, str]:
        """獲取 WooCommerce 配置"""
        return self.woocommerce_config.copy()
    
    def get_meta_config(self) -> Dict[str, str]:
        """獲取 Meta 配置"""
        return self.meta_config.copy()

def setup_api_connections():
    """設置 API 連接"""
    config = Config()
    wc_configured, meta_configured = config.is_configured()
    
    # 如果沒有配置，顯示手動輸入選項
    if not wc_configured or not meta_configured:
        st.sidebar.warning("⚠️ 請配置 API 設定")
        
        # 顯示手動輸入選項（開發/測試用）
        if st.sidebar.checkbox("手動輸入 API 設定（僅供測試）"):
            with st.sidebar.expander("WooCommerce API", expanded=not wc_configured):
                manual_wc_url = st.text_input("商店網址", placeholder="https://your-store.com", key="manual_wc_url")
                manual_wc_key = st.text_input("Consumer Key", type="password", key="manual_wc_key")
                manual_wc_secret = st.text_input("Consumer Secret", type="password", key="manual_wc_secret")
                
                if manual_wc_url and manual_wc_key and manual_wc_secret:
                    # 臨時存儲到 session state
                    st.session_state.manual_wc_config = {
                        'url': manual_wc_url,
                        'consumer_key': manual_wc_key,
                        'consumer_secret': manual_wc_secret
                    }
                    wc_configured = True
            
            with st.sidebar.expander("Meta API", expanded=not meta_configured):
                manual_meta_app_id = st.text_input("App ID", key="manual_meta_app_id")
                manual_meta_secret = st.text_input("App Secret", type="password", key="manual_meta_secret")
                manual_meta_account = st.text_input("Account ID", placeholder="act_xxxxxxxxx", key="manual_meta_account")
                
                if manual_meta_app_id and manual_meta_secret and manual_meta_account:
                    st.session_state.manual_meta_config = {
                        'app_id': manual_meta_app_id,
                        'app_secret': manual_meta_secret,
                        'account_id': manual_meta_account,
                        'long_lived_token': ''
                    }
                    meta_configured = True
    
    return wc_configured, meta_configured

def get_active_config():
    """獲取當前活動配置"""
    config = Config()
    
    # 獲取基本配置
    wc_config = config.get_woocommerce_config()
    meta_config = config.get_meta_config()
    
    # 如果有手動輸入的配置，使用手動配置覆蓋
    if hasattr(st.session_state, 'manual_wc_config') and st.session_state.manual_wc_config:
        wc_config.update(st.session_state.manual_wc_config)
    
    if hasattr(st.session_state, 'manual_meta_config') and st.session_state.manual_meta_config:
        meta_config.update(st.session_state.manual_meta_config)
    
    return wc_config, meta_config