"""
Configuration Management Module for Ecommerce Dashboard
Handles API configurations for WooCommerce and Meta APIs
"""

import streamlit as st
import os
from typing import Dict, Any, Optional, Tuple


class Config:
    """Configuration management class for API settings"""
    
    def __init__(self):
        self.woocommerce_config = None
        self.meta_config = None
        self._load_secrets()
    
    def _load_secrets(self):
        """Load configuration from Streamlit secrets"""
        try:
            # WooCommerce configuration
            if hasattr(st, 'secrets') and 'woocommerce' in st.secrets:
                self.woocommerce_config = {
                    'url': st.secrets.woocommerce.get('url', ''),
                    'consumer_key': st.secrets.woocommerce.get('consumer_key', ''),
                    'consumer_secret': st.secrets.woocommerce.get('consumer_secret', ''),
                    'version': st.secrets.woocommerce.get('version', 'wc/v3')
                }
            
            # Meta API configuration
            if hasattr(st, 'secrets') and 'meta' in st.secrets:
                self.meta_config = {
                    'access_token': st.secrets.meta.get('access_token', ''),
                    'app_id': st.secrets.meta.get('app_id', ''),
                    'app_secret': st.secrets.meta.get('app_secret', ''),
                    'ad_account_id': st.secrets.meta.get('ad_account_id', ''),
                    'api_version': st.secrets.meta.get('api_version', 'v18.0')
                }
        except Exception as e:
            st.warning(f"Error loading secrets: {str(e)}")
    
    def get_woocommerce_config(self) -> Dict[str, Any]:
        """
        Get WooCommerce API configuration from secrets
        
        Returns:
            Dict containing WooCommerce API settings
        """
        if self.woocommerce_config:
            return self.woocommerce_config.copy()
        return {}
    
    def get_meta_config(self) -> Dict[str, Any]:
        """
        Get Meta API configuration from secrets
        
        Returns:
            Dict containing Meta API settings
        """
        if self.meta_config:
            return self.meta_config.copy()
        return {}
    
    def is_configured(self) -> Tuple[bool, bool]:
        """
        Check if APIs are configured
        
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
            self.meta_config.get('access_token') and
            self.meta_config.get('app_id') and
            self.meta_config.get('app_secret')
        )
        
        return woocommerce_configured, meta_configured


def setup_api_connections() -> Dict[str, Any]:
    """
    Setup API connections with configuration check and manual input options
    
    Returns:
        Dict containing connection status and configurations
    """
    config = Config()
    woocommerce_configured, meta_configured = config.is_configured()
    
    # Initialize session state for manual configurations
    if 'manual_woocommerce_config' not in st.session_state:
        st.session_state.manual_woocommerce_config = {}
    if 'manual_meta_config' not in st.session_state:
        st.session_state.manual_meta_config = {}
    
    connection_status = {
        'woocommerce_configured': woocommerce_configured,
        'meta_configured': meta_configured,
        'woocommerce_config': config.get_woocommerce_config(),
        'meta_config': config.get_meta_config()
    }
    
    # Display configuration status
    st.subheader("🔧 API Configuration Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if woocommerce_configured:
            st.success("✅ WooCommerce API configured")
        else:
            st.error("❌ WooCommerce API not configured")
    
    with col2:
        if meta_configured:
            st.success("✅ Meta API configured")
        else:
            st.error("❌ Meta API not configured")
    
    # Manual configuration section
    if not woocommerce_configured or not meta_configured:
        st.subheader("📝 Manual Configuration")
        st.info("Configure APIs manually if secrets are not available")
        
        # WooCommerce manual configuration
        if not woocommerce_configured:
            st.subheader("🛒 WooCommerce API Setup")
            with st.expander("WooCommerce Configuration", expanded=True):
                woocommerce_url = st.text_input(
                    "Store URL",
                    value=st.session_state.manual_woocommerce_config.get('url', ''),
                    help="Your WooCommerce store URL (e.g., https://yourstore.com)"
                )
                woocommerce_key = st.text_input(
                    "Consumer Key",
                    value=st.session_state.manual_woocommerce_config.get('consumer_key', ''),
                    type="password"
                )
                woocommerce_secret = st.text_input(
                    "Consumer Secret",
                    value=st.session_state.manual_woocommerce_config.get('consumer_secret', ''),
                    type="password"
                )
                woocommerce_version = st.selectbox(
                    "API Version",
                    options=['wc/v3', 'wc/v2', 'wc/v1'],
                    index=0
                )
                
                if st.button("Save WooCommerce Config"):
                    st.session_state.manual_woocommerce_config = {
                        'url': woocommerce_url,
                        'consumer_key': woocommerce_key,
                        'consumer_secret': woocommerce_secret,
                        'version': woocommerce_version
                    }
                    st.success("WooCommerce configuration saved!")
                    st.rerun()
        
        # Meta API manual configuration
        if not meta_configured:
            st.subheader("📱 Meta API Setup")
            with st.expander("Meta API Configuration", expanded=True):
                meta_token = st.text_input(
                    "Access Token",
                    value=st.session_state.manual_meta_config.get('access_token', ''),
                    type="password",
                    help="Your Meta API access token"
                )
                meta_app_id = st.text_input(
                    "App ID",
                    value=st.session_state.manual_meta_config.get('app_id', '')
                )
                meta_app_secret = st.text_input(
                    "App Secret",
                    value=st.session_state.manual_meta_config.get('app_secret', ''),
                    type="password"
                )
                meta_ad_account = st.text_input(
                    "Ad Account ID",
                    value=st.session_state.manual_meta_config.get('ad_account_id', ''),
                    help="Your Meta Ad Account ID"
                )
                meta_version = st.selectbox(
                    "API Version",
                    options=['v18.0', 'v17.0', 'v16.0'],
                    index=0
                )
                
                if st.button("Save Meta Config"):
                    st.session_state.manual_meta_config = {
                        'access_token': meta_token,
                        'app_id': meta_app_id,
                        'app_secret': meta_app_secret,
                        'ad_account_id': meta_ad_account,
                        'api_version': meta_version
                    }
                    st.success("Meta API configuration saved!")
                    st.rerun()
    
    return connection_status


def get_active_config() -> Dict[str, Any]:
    """
    Get current active configuration (prioritizes secrets, falls back to manual input)
    
    Returns:
        Dict containing active configurations for both APIs
    """
    config = Config()
    woocommerce_configured, meta_configured = config.is_configured()
    
    # Get WooCommerce config (secrets first, then manual)
    woocommerce_config = config.get_woocommerce_config()
    if not woocommerce_configured and 'manual_woocommerce_config' in st.session_state:
        woocommerce_config = st.session_state.manual_woocommerce_config
    
    # Get Meta config (secrets first, then manual)
    meta_config = config.get_meta_config()
    if not meta_configured and 'manual_meta_config' in st.session_state:
        meta_config = st.session_state.manual_meta_config
    
    return {
        'woocommerce': woocommerce_config,
        'meta': meta_config,
        'woocommerce_configured': woocommerce_configured or bool(woocommerce_config.get('url')),
        'meta_configured': meta_configured or bool(meta_config.get('access_token'))
    }


def validate_config(config_dict: Dict[str, Any], api_type: str) -> bool:
    """
    Validate configuration dictionary
    
    Args:
        config_dict: Configuration dictionary to validate
        api_type: Type of API ('woocommerce' or 'meta')
    
    Returns:
        True if configuration is valid, False otherwise
    """
    if api_type == 'woocommerce':
        required_fields = ['url', 'consumer_key', 'consumer_secret']
        return all(config_dict.get(field) for field in required_fields)
    
    elif api_type == 'meta':
        required_fields = ['access_token', 'app_id', 'app_secret']
        return all(config_dict.get(field) for field in required_fields)
    
    return False


def clear_manual_config():
    """Clear manual configuration from session state"""
    if 'manual_woocommerce_config' in st.session_state:
        del st.session_state.manual_woocommerce_config
    if 'manual_meta_config' in st.session_state:
        del st.session_state.manual_meta_config
    st.success("Manual configurations cleared!")
    st.rerun()
