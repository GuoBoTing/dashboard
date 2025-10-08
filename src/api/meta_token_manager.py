"""
Meta Token 自動管理模組
負責：短期 token → 長期 token 轉換、自動更新、持久化儲存
"""
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import os


class MetaTokenManager:
    """Meta Token 自動管理器（支援雲端部署）"""

    def __init__(self, app_id: str, app_secret: str, storage_mode: str = "auto"):
        """
        初始化 Token 管理器

        Args:
            app_id: Meta App ID
            app_secret: Meta App Secret
            storage_mode: 儲存模式
                - "auto": 自動偵測（優先 secrets，其次 session，最後 file）
                - "secrets": 使用 Streamlit Secrets（適合雲端部署）
                - "session": 僅使用 Session State（重啟會失效）
                - "file": 使用本地檔案（適合本地開發）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.storage_mode = storage_mode
        self.exchange_url = "https://graph.facebook.com/v23.0/oauth/access_token"
        self.debug_url = "https://graph.facebook.com/v23.0/debug_token"

        # 自動偵測儲存模式
        if storage_mode == "auto":
            self.storage_mode = self._detect_storage_mode()

        # 本地檔案路徑（僅在 file 模式使用）
        self.storage_path = Path(".streamlit/meta_token.json")
        if self.storage_mode == "file":
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _detect_storage_mode(self) -> str:
        """
        自動偵測最佳儲存模式

        Returns:
            "secrets" | "session" | "file"
        """
        # 檢查是否在雲端環境（Zeabur, Streamlit Cloud 等）
        is_cloud = os.getenv('ZEABUR_SERVICE_ID') or os.getenv('STREAMLIT_SHARING_MODE')

        if is_cloud:
            # 雲端環境優先使用 session（因為 secrets 需要手動設定）
            return "session"
        else:
            # 本地環境使用檔案
            return "file"

    def exchange_short_to_long_token(self, short_token: str) -> Dict:
        """
        將短期 token 轉換為長期 token

        Args:
            short_token: 短期 access token（從 Meta Graph API Explorer 取得）

        Returns:
            包含長期 token 資訊的字典
        """
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_token
        }

        try:
            response = requests.get(self.exchange_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 計算過期時間
            expires_in = data.get('expires_in', 5183944)  # 預設 60 天
            expires_at = datetime.now() + timedelta(seconds=expires_in)

            token_info = {
                'access_token': data['access_token'],
                'token_type': data.get('token_type', 'bearer'),
                'expires_in': expires_in,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now().isoformat()
            }

            # 自動儲存
            self.save_token(token_info)

            return token_info

        except requests.exceptions.RequestException as e:
            raise Exception(f"轉換長期 token 失敗: {str(e)}")

    def refresh_token(self, current_token: str) -> Dict:
        """
        刷新長期 token（延長有效期）

        Args:
            current_token: 當前的長期 token

        Returns:
            新的 token 資訊
        """
        # Meta 長期 token 可以用自己換自己來刷新
        return self.exchange_short_to_long_token(current_token)

    def get_token_info(self, access_token: str) -> Dict:
        """
        取得 token 的詳細資訊（用於檢查有效性）

        Args:
            access_token: 要檢查的 token

        Returns:
            Token 資訊字典
        """
        params = {
            'input_token': access_token,
            'access_token': f"{self.app_id}|{self.app_secret}"
        }

        try:
            response = requests.get(self.debug_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"取得 token 資訊失敗: {str(e)}")

    def is_token_valid(self, token_data: Dict) -> bool:
        """
        檢查 token 是否仍然有效

        Args:
            token_data: 從 load_token() 取得的 token 資料

        Returns:
            True 如果有效，False 如果已過期
        """
        if not token_data or 'expires_at' not in token_data:
            return False

        expires_at = datetime.fromisoformat(token_data['expires_at'])
        # 提前 7 天判定為即將過期
        buffer_time = timedelta(days=7)

        return datetime.now() < (expires_at - buffer_time)

    def save_token(self, token_data: Dict) -> None:
        """
        儲存 token（根據儲存模式選擇儲存位置）

        Args:
            token_data: Token 資料字典
        """
        try:
            if self.storage_mode == "session":
                # 儲存到 Session State
                st.session_state.meta_token_data = token_data

            elif self.storage_mode == "file":
                # 儲存到本地檔案
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(token_data, f, indent=2, ensure_ascii=False)

            elif self.storage_mode == "secrets":
                # Secrets 是唯讀的，只能顯示警告
                st.session_state.meta_token_data = token_data
                st.info("💡 提示：如需長期儲存，請將 Token 加入 Zeabur 環境變數")

        except Exception as e:
            st.warning(f"儲存 token 失敗: {str(e)}")

    def load_token(self) -> Optional[Dict]:
        """
        載入 token（根據儲存模式從不同位置載入）
        優先順序：Session State > 環境變數 > File > Secrets

        Returns:
            Token 資料字典，如果不存在則返回 None
        """
        try:
            # 1. 優先從 Session State 載入（所有模式都適用）
            if 'meta_token_data' in st.session_state:
                return st.session_state.meta_token_data

            # 2. 從環境變數載入（適合 Zeabur 等雲端平台）
            env_token = os.getenv('META_LONG_LIVED_TOKEN')
            if env_token:
                # 從環境變數建立 token 資料
                # 設定為永不過期（實際上 Meta Token 有 60 天期限，但由使用者手動更新）
                expires_at = datetime.now() + timedelta(days=365)  # 設定為 1 年後，避免自動刷新
                token_data = {
                    'access_token': env_token.strip(),  # 去除可能的空白字元
                    'expires_at': expires_at.isoformat(),
                    'expires_in': 31536000,  # 1 年（秒）
                    'created_at': datetime.now().isoformat(),
                    'from_env': True  # 標記為來自環境變數
                }
                # 快取到 session
                st.session_state.meta_token_data = token_data
                return token_data

            # 3. 根據儲存模式載入
            if self.storage_mode == "file":
                # 從本地檔案載入
                if not self.storage_path.exists():
                    return None
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            elif self.storage_mode == "secrets":
                # 從 secrets 讀取（如果有設定）
                if hasattr(st, 'secrets') and 'meta_token' in st.secrets:
                    token_secrets = st.secrets.meta_token
                    return {
                        'access_token': token_secrets.get('access_token'),
                        'expires_at': token_secrets.get('expires_at'),
                        'expires_in': token_secrets.get('expires_in', 5183944),
                        'created_at': token_secrets.get('created_at')
                    }

            return None

        except Exception as e:
            st.warning(f"載入 token 失敗: {str(e)}")
            return None

    def delete_token(self) -> None:
        """刪除儲存的 token"""
        try:
            if self.storage_mode == "session":
                if 'meta_token_data' in st.session_state:
                    del st.session_state.meta_token_data

            elif self.storage_mode == "file":
                if self.storage_path.exists():
                    self.storage_path.unlink()

            elif self.storage_mode == "secrets":
                if 'meta_token_data' in st.session_state:
                    del st.session_state.meta_token_data
                st.warning("⚠️ Secrets 中的 Token 需要手動從 Zeabur 環境變數中刪除")

        except Exception as e:
            st.warning(f"刪除 token 失敗: {str(e)}")

    def get_valid_token(self) -> Optional[str]:
        """
        取得有效的 token（自動檢查並刷新）

        Returns:
            有效的 access token，如果無法取得則返回 None
        """
        # 1. 先從檔案載入
        token_data = self.load_token()

        if not token_data:
            return None

        # 2. 如果是來自環境變數的 Token，直接返回（不自動刷新）
        if token_data.get('from_env'):
            return token_data['access_token']

        # 3. 檢查是否有效
        if self.is_token_valid(token_data):
            return token_data['access_token']

        # 4. 如果即將過期，嘗試自動刷新（僅限非環境變數的 Token）
        try:
            st.info("🔄 Token 即將過期，正在自動刷新...")
            new_token_data = self.refresh_token(token_data['access_token'])
            st.success("✅ Token 已自動更新！")
            return new_token_data['access_token']

        except Exception as e:
            st.error(f"❌ Token 自動更新失敗: {str(e)}")
            st.warning("請手動輸入新的短期 token 來更新")
            return None


def show_token_manager_ui(app_id: str, app_secret: str) -> Optional[str]:
    """
    顯示 Token 管理 UI（簡化版本，無 OAuth，支援雲端部署）

    Args:
        app_id: Meta App ID
        app_secret: Meta App Secret

    Returns:
        有效的 access token，如果沒有則返回 None
    """
    st.subheader("🔑 Meta Token 管理")

    manager = MetaTokenManager(app_id, app_secret)

    # 顯示儲存模式資訊
    storage_mode_emoji = {
        "file": "💾",
        "session": "🔄",
        "secrets": "🔒"
    }
    storage_mode_desc = {
        "file": "本地檔案（開發環境）",
        "session": "Session State（雲端部署）",
        "secrets": "Streamlit Secrets"
    }
    st.caption(f"{storage_mode_emoji.get(manager.storage_mode, '📦')} 儲存模式: {storage_mode_desc.get(manager.storage_mode, manager.storage_mode)}")

    # 雲端部署提示
    if manager.storage_mode == "session":
        st.info("💡 雲端部署模式：Token 會在服務重啟後消失，建議將長期 Token 加入環境變數")

    # 嘗試取得有效的 token
    current_token = manager.get_valid_token()

    # 顯示目前狀態
    token_data = manager.load_token()

    if token_data and current_token:
        # Token 有效
        st.success("✅ Token 已設定且有效")

        col1, col2, col3 = st.columns(3)

        with col1:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            days_left = (expires_at - datetime.now()).days
            st.metric("剩餘天數", f"{days_left} 天")

        with col2:
            created_at = datetime.fromisoformat(token_data['created_at'])
            st.metric("建立日期", created_at.strftime("%Y-%m-%d"))

        with col3:
            if st.button("🔄 手動更新 Token"):
                try:
                    with st.spinner("更新中..."):
                        new_data = manager.refresh_token(current_token)
                        st.success("✅ Token 已更新！")
                        st.rerun()
                except Exception as e:
                    st.error(f"更新失敗: {str(e)}")

        # 顯示 Token（摺疊）
        with st.expander("🔍 查看 Token 資訊"):
            # 顯示完整 Token（可複製）
            st.text_area(
                "完整 Access Token（可複製）",
                value=current_token,
                height=100,
                help="請複製此 Token 到 Zeabur 環境變數"
            )

            st.caption(f"Token 長度: {len(current_token)} 字元")
            st.caption(f"開頭: {current_token[:20]}...")
            st.caption(f"結尾: ...{current_token[-20:]}")

            # Zeabur 環境變數設定提示
            if manager.storage_mode == "session":
                st.markdown("---")
                st.markdown("**💾 長期儲存到 Zeabur 環境變數：**")
                st.code(f"META_LONG_LIVED_TOKEN={current_token}", language="bash")
                st.caption("⚠️ 複製上方完整 Token 到 Zeabur → Variables → META_LONG_LIVED_TOKEN")
            else:
                st.markdown("---")
                st.markdown("**💾 設定到 Zeabur（如需雲端部署）：**")
                st.caption("1. 複製上方完整 Token")
                st.caption("2. 在 Zeabur Variables 中新增 META_LONG_LIVED_TOKEN")
                st.caption("3. 貼上 Token 並儲存")

            if st.button("🗑️ 刪除 Token"):
                manager.delete_token()
                st.success("Token 已刪除")
                st.rerun()

    else:
        # 需要設定 Token
        st.info("請輸入短期 Token，系統將自動轉換為長期 Token（60 天有效期）")

        st.markdown("""
        **📝 如何取得短期 Token：**
        1. 前往 [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/)
        2. 選擇你的應用程式
        3. 在「權限」中勾選：`ads_read`、`ads_management`
        4. 點擊「產生存取權杖」
        5. 複製 Token 並貼到下方
        """)

        short_token = st.text_input(
            "短期 Access Token",
            type="password",
            placeholder="請貼上從 Graph API Explorer 取得的 token"
        )

        if st.button("🔄 轉換為長期 Token", type="primary"):
            if short_token:
                try:
                    with st.spinner("轉換中..."):
                        token_data = manager.exchange_short_to_long_token(short_token)
                        st.success(f"✅ 轉換成功！Token 有效期約 {token_data['expires_in'] // 86400} 天")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 轉換失敗: {str(e)}")
                    st.info("請確認：\n1. Token 是否正確\n2. App ID 和 App Secret 是否正確\n3. Token 權限是否包含 ads_read")
            else:
                st.warning("請輸入短期 Token")

    return current_token
