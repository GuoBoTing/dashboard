# oauth_example.py - OAuth 整合範例
"""
這是一個示範如何在 app.py 中整合 OAuth 的範例檔案

使用方式：
1. 將此檔案的程式碼片段複製到 app.py
2. 或直接執行此檔案測試 OAuth: streamlit run oauth_example.py
"""

import streamlit as st
from meta_oauth import show_oauth_login_ui, get_oauth_token, is_oauth_authenticated
import os

# 頁面設定
st.set_page_config(
    page_title="Meta OAuth 範例",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Meta OAuth 2.0 整合範例")

# 側邊欄 - OAuth 設定
with st.sidebar:
    st.header("Meta API 認證")

    # 從環境變數或 secrets 取得設定
    try:
        if hasattr(st, 'secrets') and 'meta' in st.secrets:
            app_id = st.secrets.meta.app_id
            app_secret = st.secrets.meta.app_secret
            redirect_uri = st.secrets.meta.get('oauth_redirect_uri', 'http://localhost:8501')
        else:
            app_id = os.getenv('META_APP_ID', '')
            app_secret = os.getenv('META_APP_SECRET', '')
            redirect_uri = os.getenv('META_OAUTH_REDIRECT_URI', 'http://localhost:8501')

        # 檢查設定是否完整
        if not app_id or not app_secret:
            st.error("⚠️ 請先設定 META_APP_ID 和 META_APP_SECRET")
            st.info("請在 `.streamlit/secrets.toml` 或 `.env` 中設定")
            st.stop()

        # 顯示 OAuth 登入 UI
        show_oauth_login_ui(app_id, app_secret, redirect_uri)

    except Exception as e:
        st.error(f"設定載入失敗: {str(e)}")
        st.stop()

# 主要內容
st.markdown("---")

# 檢查認證狀態
if is_oauth_authenticated():
    st.success("✅ 已透過 OAuth 認證")

    # 取得 token
    token = get_oauth_token()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("認證資訊")
        token_info = st.session_state.get('meta_oauth_token', {})
        st.write(f"**使用者**: {token_info.get('user_name', 'Unknown')}")
        st.write(f"**User ID**: {token_info.get('user_id', 'Unknown')}")
        st.write(f"**Token 有效期**: 約 {token_info.get('expires_in', 0) // 86400} 天")

    with col2:
        st.subheader("Token 預覽")
        if token:
            st.code(f"{token[:50]}...", language="text")
            st.caption("前 50 個字元")

    st.markdown("---")

    # 示範如何使用 token 呼叫 API
    st.subheader("📊 測試 Meta Ads API")

    account_id = st.text_input(
        "輸入廣告帳號 ID",
        placeholder="act_123456789",
        help="在 Meta 廣告管理員中可以找到"
    )

    if st.button("測試 API 連接") and account_id:
        import requests

        with st.spinner("正在測試 API..."):
            try:
                # 測試取得帳號資訊
                url = f"https://graph.facebook.com/v23.0/{account_id}"
                params = {
                    'access_token': token,
                    'fields': 'name,account_status,currency,amount_spent'
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                st.success("✅ API 連接成功！")

                # 顯示帳號資訊
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("帳號名稱", data.get('name', 'N/A'))

                with col2:
                    st.metric("帳號狀態", data.get('account_status', 'N/A'))

                with col3:
                    st.metric("累計消費", f"${data.get('amount_spent', 0)}")

                # 顯示完整響應
                with st.expander("查看完整 API 響應"):
                    st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"❌ API 請求失敗: {str(e)}")
                if hasattr(e, 'response') and e.response:
                    st.error(f"響應內容: {e.response.text}")

else:
    st.info("👈 請先在側邊欄使用 Meta OAuth 登入")

    st.markdown("""
    ### 🚀 快速開始

    1. **設定 Meta 應用程式**
       - 前往 [Meta 開發者平台](https://developers.facebook.com/apps/)
       - 在「Facebook 登入」設定中新增 OAuth Redirect URI: `http://localhost:8501`

    2. **設定環境變數**
       ```bash
       META_APP_ID=你的_app_id
       META_APP_SECRET=你的_app_secret
       META_OAUTH_REDIRECT_URI=http://localhost:8501
       ```

    3. **點擊側邊欄的「使用 Meta 登入」按鈕**

    4. **在 Meta 頁面授權應用程式**

    5. **自動返回並取得長期 Token！**

    ---

    ### 📚 詳細文件

    - [OAUTH_SETUP.md](OAUTH_SETUP.md) - OAuth 完整設定指南
    - [META_TOKEN_SETUP.md](META_TOKEN_SETUP.md) - Token 管理說明

    ---

    ### 💡 優勢

    | 傳統方式 | OAuth 2.0 |
    |---------|-----------|
    | 需要手動複製 token | ✅ 自動取得 |
    | 需要去 Graph API Explorer | ✅ 直接在應用中登入 |
    | 複雜且容易出錯 | ✅ 簡單直觀 |
    | 較差的使用者體驗 | ✅ 專業的登入流程 |
    """)

# 頁腳
st.markdown("---")
st.caption("🔐 OAuth 2.0 整合範例 | Flambé Dashboard v2.0")