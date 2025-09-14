"""
Enhanced Meta Ads API Client
Provides comprehensive functionality for Meta Ads API integration
"""

import streamlit as st
import requests
import pandas as pd
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
import time
from urllib.parse import urlencode


class MetaAdsAPI:
    """Enhanced Meta Ads API client with token management and error handling"""
    
    def __init__(self, app_id: str, app_secret: str, account_id: str, long_lived_token: str):
        """
        Initialize Meta Ads API client
        
        Args:
            app_id: Meta App ID
            app_secret: Meta App Secret
            account_id: Meta Ad Account ID
            long_lived_token: Long-lived access token
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.account_id = account_id
        self.long_lived_token = long_lived_token
        self.base_url = "https://graph.facebook.com"
        self.api_version = "v18.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetaAdsAPI-Client/1.0',
            'Content-Type': 'application/json'
        })
        
        # Token expiration tracking
        self.token_expires_at = None
        self.last_token_refresh = None
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                     method: str = 'GET', max_retries: int = 3) -> Dict[str, Any]:
        """
        Make HTTP request with retry mechanism and error handling
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            method: HTTP method
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response as dictionary
        """
        if params is None:
            params = {}
        
        # Add access token to parameters
        params['access_token'] = self.long_lived_token
        
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=params, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    st.warning(f"Request timeout. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Request timeout after multiple attempts")
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    # Token might be expired, try to refresh
                    st.warning("Token may be expired. Attempting to refresh...")
                    if self._validate_and_refresh_token():
                        # Retry with refreshed token
                        params['access_token'] = self.long_lived_token
                        continue
                    else:
                        raise Exception("Failed to refresh token")
                elif e.response.status_code == 429:
                    # Rate limit exceeded
                    if attempt < max_retries - 1:
                        wait_time = 60 * (attempt + 1)  # Wait longer for rate limits
                        st.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after multiple attempts")
                else:
                    error_data = e.response.json() if e.response.content else {}
                    error_message = error_data.get('error', {}).get('message', str(e))
                    raise Exception(f"HTTP Error {e.response.status_code}: {error_message}")
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    st.warning(f"Request failed: {str(e)}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Request failed after multiple attempts: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def refresh_long_lived_token(self) -> bool:
        """
        Refresh long-lived access token
        
        Returns:
            True if token was refreshed successfully, False otherwise
        """
        try:
            endpoint = "oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': self.long_lived_token
            }
            
            response = self._make_request(endpoint, params)
            
            if 'access_token' in response:
                self.long_lived_token = response['access_token']
                expires_in = response.get('expires_in', 0)
                self.token_expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
                self.last_token_refresh = datetime.datetime.now()
                return True
            else:
                st.error("Failed to refresh token: No access token in response")
                return False
                
        except Exception as e:
            st.error(f"Error refreshing token: {str(e)}")
            return False
    
    def _validate_and_refresh_token(self) -> bool:
        """
        Validate token and refresh if necessary
        
        Returns:
            True if token is valid or was refreshed successfully
        """
        try:
            # Test token validity by making a simple API call
            endpoint = f"act_{self.account_id}"
            params = {'fields': 'id,name'}
            
            response = self._make_request(endpoint, params)
            
            if 'id' in response:
                return True
            else:
                return False
                
        except Exception:
            # Token is invalid, try to refresh
            return self.refresh_long_lived_token()
    
    def get_ads_insights(self, date_preset: str = 'last_30d', 
                        fields: List[str] = None, 
                        breakdowns: List[str] = None,
                        level: str = 'campaign') -> Dict[str, Any]:
        """
        Get ads insights data
        
        Args:
            date_preset: Date range preset (e.g., 'last_30d', 'last_7d')
            fields: List of fields to retrieve
            breakdowns: List of breakdown dimensions
            level: Data level (campaign, adset, ad)
            
        Returns:
            Ads insights data
        """
        if fields is None:
            fields = [
                'impressions', 'clicks', 'spend', 'reach', 'frequency',
                'cpm', 'cpc', 'ctr', 'cpm', 'cost_per_result',
                'actions', 'action_values', 'conversion_values'
            ]
        
        if breakdowns is None:
            breakdowns = []
        
        try:
            endpoint = f"act_{self.account_id}/insights"
            params = {
                'date_preset': date_preset,
                'fields': ','.join(fields),
                'level': level,
                'limit': 1000
            }
            
            if breakdowns:
                params['breakdowns'] = ','.join(breakdowns)
            
            response = self._make_request(endpoint, params)
            return response
            
        except Exception as e:
            st.error(f"Error fetching ads insights: {str(e)}")
            return {'data': [], 'error': str(e)}
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test API connection
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Test basic connection
            endpoint = f"act_{self.account_id}"
            params = {'fields': 'id,name,account_status'}
            
            response = self._make_request(endpoint, params)
            
            if 'id' in response:
                account_name = response.get('name', 'Unknown')
                account_status = response.get('account_status', 'Unknown')
                return True, f"✅ Connection successful! Account: {account_name}, Status: {account_status}"
            else:
                return False, "❌ Connection failed: Invalid response"
                
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get detailed account information"""
        try:
            endpoint = f"act_{self.account_id}"
            params = {
                'fields': 'id,name,account_status,currency,timezone_name,amount_spent,balance'
            }
            
            response = self._make_request(endpoint, params)
            return response
            
        except Exception as e:
            st.error(f"Error fetching account info: {str(e)}")
            return {}


def get_enhanced_meta_ads_data(config: Dict[str, Any], 
                              date_preset: str = 'last_30d',
                              level: str = 'campaign') -> pd.DataFrame:
    """
    Get enhanced Meta Ads data using the API client
    
    Args:
        config: Meta API configuration
        date_preset: Date range preset
        level: Data level (campaign, adset, ad)
        
    Returns:
        DataFrame with ads data
    """
    try:
        # Initialize API client
        api_client = MetaAdsAPI(
            app_id=config.get('app_id', ''),
            app_secret=config.get('app_secret', ''),
            account_id=config.get('ad_account_id', ''),
            long_lived_token=config.get('access_token', '')
        )
        
        # Test connection first
        success, message = api_client.test_connection()
        if not success:
            st.error(message)
            return pd.DataFrame()
        
        st.success(message)
        
        # Get ads insights
        with st.spinner("Fetching Meta Ads data..."):
            insights_data = api_client.get_ads_insights(
                date_preset=date_preset,
                level=level
            )
        
        if 'data' in insights_data and insights_data['data']:
            # Convert to DataFrame
            df = pd.DataFrame(insights_data['data'])
            
            # Process the data
            if not df.empty:
                # Convert date columns
                if 'date_start' in df.columns:
                    df['date_start'] = pd.to_datetime(df['date_start'])
                if 'date_stop' in df.columns:
                    df['date_stop'] = pd.to_datetime(df['date_stop'])
                
                # Convert numeric columns
                numeric_columns = ['impressions', 'clicks', 'spend', 'reach', 'frequency']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Process actions data
                if 'actions' in df.columns:
                    df['actions'] = df['actions'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
                
                st.success(f"✅ Successfully fetched {len(df)} records")
                return df
            else:
                st.warning("No data found for the specified criteria")
                return pd.DataFrame()
        else:
            error_msg = insights_data.get('error', 'Unknown error')
            st.error(f"Failed to fetch data: {error_msg}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error in get_enhanced_meta_ads_data: {str(e)}")
        return pd.DataFrame()


def show_token_management():
    """Display token management interface"""
    st.subheader("🔑 Meta API Token Management")
    
    # Initialize session state for token management
    if 'meta_token_info' not in st.session_state:
        st.session_state.meta_token_info = {
            'last_refresh': None,
            'expires_at': None,
            'refresh_count': 0
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Token Information")
        
        # Display current token info
        if st.session_state.meta_token_info['last_refresh']:
            st.info(f"**Last Refresh:** {st.session_state.meta_token_info['last_refresh']}")
        
        if st.session_state.meta_token_info['expires_at']:
            st.info(f"**Expires At:** {st.session_state.meta_token_info['expires_at']}")
        
        st.info(f"**Refresh Count:** {st.session_state.meta_token_info['refresh_count']}")
    
    with col2:
        st.markdown("### Token Actions")
        
        # Manual token refresh button
        if st.button("🔄 Refresh Token", help="Manually refresh the long-lived token"):
            try:
                # Get current config
                from config import get_active_config
                active_config = get_active_config()
                meta_config = active_config.get('meta', {})
                
                if not meta_config.get('access_token'):
                    st.error("No access token found in configuration")
                else:
                    # Initialize API client for token refresh
                    api_client = MetaAdsAPI(
                        app_id=meta_config.get('app_id', ''),
                        app_secret=meta_config.get('app_secret', ''),
                        account_id=meta_config.get('ad_account_id', ''),
                        long_lived_token=meta_config.get('access_token', '')
                    )
                    
                    # Refresh token
                    if api_client.refresh_long_lived_token():
                        st.success("✅ Token refreshed successfully!")
                        st.session_state.meta_token_info['last_refresh'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.meta_token_info['refresh_count'] += 1
                        st.rerun()
                    else:
                        st.error("❌ Failed to refresh token")
                        
            except Exception as e:
                st.error(f"Error refreshing token: {str(e)}")
        
        # Test connection button
        if st.button("🔍 Test Connection", help="Test the current API connection"):
            try:
                from config import get_active_config
                active_config = get_active_config()
                meta_config = active_config.get('meta', {})
                
                if not meta_config.get('access_token'):
                    st.error("No access token found in configuration")
                else:
                    api_client = MetaAdsAPI(
                        app_id=meta_config.get('app_id', ''),
                        app_secret=meta_config.get('app_secret', ''),
                        account_id=meta_config.get('ad_account_id', ''),
                        long_lived_token=meta_config.get('access_token', '')
                    )
                    
                    success, message = api_client.test_connection()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                        
            except Exception as e:
                st.error(f"Error testing connection: {str(e)}")
    
    # Token status indicator
    st.markdown("### Token Status")
    
    # Check if token is close to expiration
    if st.session_state.meta_token_info['expires_at']:
        try:
            expires_at = datetime.datetime.strptime(
                st.session_state.meta_token_info['expires_at'], 
                "%Y-%m-%d %H:%M:%S"
            )
            time_until_expiry = expires_at - datetime.datetime.now()
            
            if time_until_expiry.total_seconds() < 86400:  # Less than 24 hours
                st.warning("⚠️ Token expires within 24 hours. Consider refreshing.")
            elif time_until_expiry.total_seconds() < 604800:  # Less than 7 days
                st.info("ℹ️ Token expires within 7 days.")
            else:
                st.success("✅ Token is valid for more than 7 days.")
        except:
            st.info("ℹ️ Token expiration time not available.")
    else:
        st.info("ℹ️ Token expiration time not set.")
    
    # API usage statistics
    st.markdown("### API Usage Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Refreshes", st.session_state.meta_token_info['refresh_count'])
    
    with col2:
        if st.session_state.meta_token_info['last_refresh']:
            last_refresh = datetime.datetime.strptime(
                st.session_state.meta_token_info['last_refresh'], 
                "%Y-%m-%d %H:%M:%S"
            )
            hours_since_refresh = (datetime.datetime.now() - last_refresh).total_seconds() / 3600
            st.metric("Hours Since Last Refresh", f"{hours_since_refresh:.1f}")
        else:
            st.metric("Hours Since Last Refresh", "N/A")
    
    with col3:
        st.metric("API Version", "v18.0")
