# meta_oauth.py - Meta OAuth 2.0 認證流程
import streamlit as st
import requests
from urllib.parse import urlencode
import secrets
from typing import Optional, Dict

class MetaOAuth:
    """Meta OAuth 2.0 認證管理器"""

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        """
        初始化 OAuth 管理器

        Args:
            app_id: Meta App ID
            app_secret: Meta App Secret
            redirect_uri: OAuth 回調 URL（必須在 Meta 應用程式設定中配置）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://www.facebook.com/v23.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v23.0/oauth/access_token"
        self.exchange_url = "https://graph.facebook.com/v23.0/oauth/access_token"

        # OAuth 權限範圍
        self.scope = [
            'ads_read',           # 讀取廣告數據
            'ads_management',     # 管理廣告（如果需要）
            'business_management' # 企業管理（如果需要）
        ]

    def get_authorization_url(self) -> tuple[str, str]:
        """
        生成 OAuth 授權 URL

        Returns:
            (authorization_url, state) - 授權 URL 和 CSRF 保護的 state 參數
        """
        # 生成隨機 state 用於 CSRF 保護
        state = secrets.token_urlsafe(32)

        # 構建授權參數
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': ','.join(self.scope),
            'response_type': 'code'  # 使用 authorization code flow
        }

        auth_url = f"{self.base_url}?{urlencode(params)}"

        return auth_url, state

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        用 authorization code 換取 access token

        Args:
            code: OAuth authorization code

        Returns:
            包含 access_token 的字典
        """
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        try:
            response = requests.get(self.token_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                'access_token': data['access_token'],
                'token_type': data.get('token_type', 'bearer'),
                'expires_in': data.get('expires_in', 3600)  # 短期 token，約1小時
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"換取 token 失敗: {str(e)}")

    def exchange_for_long_lived_token(self, short_lived_token: str) -> Dict:
        """
        將短期 token 換成長期 token

        Args:
            short_lived_token: 短期 access token

        Returns:
            包含 long-lived token 的字典
        """
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_lived_token
        }

        try:
            response = requests.get(self.exchange_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                'access_token': data['access_token'],
                'token_type': data.get('token_type', 'bearer'),
                'expires_in': data.get('expires_in', 5183944)  # 長期 token，約60天
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"換取長期 token 失敗: {str(e)}")

    def get_user_info(self, access_token: str) -> Dict:
        """
        取得使用者資訊（用於驗證 token）

        Args:
            access_token: Meta access token

        Returns:
            使用者資訊字典
        """
        url = "https://graph.facebook.com/v21.0/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,email'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"取得使用者資訊失敗: {str(e)}")


def show_oauth_login_ui(app_id: str, app_secret: str, redirect_uri: str):
    """
    顯示 OAuth 登入 UI 元件

    Args:
        app_id: Meta App ID
        app_secret: Meta App Secret
        redirect_uri: OAuth redirect URI
    """
    st.subheader("🔐 Meta OAuth 登入")

    oauth = MetaOAuth(app_id, app_secret, redirect_uri)

    # 檢查 URL 參數中是否有 authorization code
    query_params = st.query_params

    # 如果有 code 參數，表示使用者已經授權並返回
    if 'code' in query_params:
        auth_code = query_params['code']
        state_from_url = query_params.get('state', '')

        # 驗證 state（CSRF 保護）
        expected_state = st.session_state.get('oauth_state', '')

        if state_from_url != expected_state:
            st.error("⚠️ 安全驗證失敗（state 不匹配），請重新登入")
            return

        # 顯示處理中訊息
        with st.spinner("正在處理授權..."):
            try:
                # 步驟 1: 用 code 換取短期 token
                st.info("步驟 1/3: 換取短期 token...")
                short_token_info = oauth.exchange_code_for_token(auth_code)
                short_token = short_token_info['access_token']

                # 步驟 2: 換取長期 token
                st.info("步驟 2/3: 換取長期 token...")
                long_token_info = oauth.exchange_for_long_lived_token(short_token)
                long_token = long_token_info['access_token']

                # 步驟 3: 驗證 token 並取得使用者資訊
                st.info("步驟 3/3: 驗證 token...")
                user_info = oauth.get_user_info(long_token)

                # 保存到 session state
                st.session_state.meta_oauth_token = {
                    'access_token': long_token,
                    'expires_in': long_token_info['expires_in'],
                    'user_name': user_info.get('name', 'Unknown'),
                    'user_id': user_info.get('id', 'Unknown')
                }

                # 清除 URL 參數
                st.query_params.clear()

                st.success(f"✅ 登入成功！歡迎 {user_info.get('name', 'User')}")
                st.success(f"🎉 長期 Token 已取得（有效期約 {long_token_info['expires_in'] // 86400} 天）")

                # 顯示 token 資訊（可選）
                with st.expander("查看 Token 資訊"):
                    st.code(long_token, language="text")
                    st.caption("請妥善保管此 token，它將用於存取 Meta Ads API")

                # 提示重新整理
                st.info("請點擊下方按鈕繼續使用儀表板")
                if st.button("開始使用儀表板"):
                    st.rerun()

            except Exception as e:
                st.error(f"❌ OAuth 認證失敗: {str(e)}")
                st.info("請重新點擊登入按鈕")

                # 清除錯誤的參數
                st.query_params.clear()
                if st.button("重新登入"):
                    st.rerun()

    # 如果已經登入
    elif 'meta_oauth_token' in st.session_state:
        token_info = st.session_state.meta_oauth_token

        st.success(f"✅ 已登入: {token_info.get('user_name', 'User')}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Token 狀態", "有效")
            st.caption(f"有效期: 約 {token_info.get('expires_in', 0) // 86400} 天")

        with col2:
            if st.button("登出"):
                del st.session_state.meta_oauth_token
                if 'oauth_state' in st.session_state:
                    del st.session_state.oauth_state
                st.rerun()

    # 初始狀態：顯示登入按鈕
    else:
        st.info("透過 Meta OAuth 2.0 登入，自動取得長期 Access Token")

        st.markdown("""
        **登入流程：**
        1. 點擊下方「使用 Meta 登入」按鈕
        2. 在 Meta 登入頁面授權應用程式
        3. 自動返回並取得長期 Token（有效期約 60 天）
        4. Token 將自動用於 Meta Ads API 請求
        """)

        # 生成授權 URL
        auth_url, state = oauth.get_authorization_url()

        # 保存 state 到 session（CSRF 保護）
        st.session_state.oauth_state = state

        # 顯示登入按鈕
        st.markdown(f"""
        <a href="{auth_url}" target="_self">
            <button style="
                background-color: #1877f2;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
            ">
                🔐 使用 Meta 登入
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.caption("⚠️ 首次登入需要在 Meta 開發者平台設定 OAuth Redirect URI")


def get_oauth_token() -> Optional[str]:
    """
    取得當前的 OAuth token

    Returns:
        access_token 或 None
    """
    if 'meta_oauth_token' in st.session_state:
        return st.session_state.meta_oauth_token.get('access_token')
    return None


def is_oauth_authenticated() -> bool:
    """
    檢查是否已透過 OAuth 認證

    Returns:
        True if authenticated, False otherwise
    """
    return 'meta_oauth_token' in st.session_state