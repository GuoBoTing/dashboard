# Meta OAuth 2.0 設定指南

## 🎯 為什麼要用 OAuth？

傳統方式需要：
1. ❌ 手動去 Graph API Explorer
2. ❌ 選擇應用程式和權限
3. ❌ 複製短期 token
4. ❌ 貼到 UI 換取長期 token

**使用 OAuth 後**：
1. ✅ 點擊「使用 Meta 登入」按鈕
2. ✅ Meta 頁面授權
3. ✅ 自動取得長期 token（60天）
4. ✅ 完成！

---

## 📋 前置準備

### 1. 在 Meta 開發者平台設定應用程式

前往 [Meta 開發者平台](https://developers.facebook.com/apps/)

#### 步驟 1：建立或選擇應用程式

如果還沒有應用程式：
- 點擊「建立應用程式」
- 選擇「商業」類型
- 填寫應用程式名稱

#### 步驟 2：新增產品

在應用程式儀表板：
1. 找到「新增產品」
2. 選擇「Facebook 登入」
3. 選擇「Web」平台

#### 步驟 3：設定 OAuth Redirect URI

這是**最重要**的步驟！

1. 前往「Facebook 登入」→「設定」
2. 找到「有效的 OAuth 重新導向 URI」
3. 新增你的 Redirect URI：

**本地開發**：
```
http://localhost:8501
```

**Streamlit Cloud 部署**：
```
https://your-app-name.streamlit.app
```

4. 點擊「儲存變更」

#### 步驟 4：取得 App ID 和 App Secret

1. 前往「設定」→「基本資料」
2. 複製「應用程式編號」(App ID)
3. 點擊「顯示」查看「應用程式密鑰」(App Secret)

#### 步驟 5：設定廣告 API 權限

1. 前往「應用程式審查」→「權限和功能」
2. 請求以下權限：
   - `ads_read` - 讀取廣告數據（必要）
   - `ads_management` - 管理廣告（可選）
   - `business_management` - 企業管理（可選）

⚠️ **注意**：部分權限需要 Meta 審核才能使用

---

## 🔧 本地配置

### 方法 1：使用 `.env` 檔案

編輯 `.env`：
```bash
# Meta OAuth 設定
META_APP_ID=你的_app_id
META_APP_SECRET=你的_app_secret
META_ACCOUNT_ID=act_你的廣告帳號ID

# OAuth Redirect URI
META_OAUTH_REDIRECT_URI=http://localhost:8501
```

### 方法 2：使用 Streamlit Secrets

編輯 `.streamlit/secrets.toml`：
```toml
[meta]
app_id = "你的_app_id"
app_secret = "你的_app_secret"
account_id = "act_123456789"
oauth_redirect_uri = "http://localhost:8501"
```

---

## 🚀 整合到應用程式

### 在 app.py 中使用 OAuth

編輯 `app.py`，加入 OAuth 登入選項：

```python
# 在檔案開頭加入
from meta_oauth import show_oauth_login_ui, get_oauth_token, is_oauth_authenticated

# 在側邊欄中加入 OAuth 登入
with st.sidebar:
    st.header("設定面板")
    st.markdown("---")

    # 選擇認證方式
    auth_method = st.radio(
        "Meta API 認證方式",
        ["OAuth 登入 (推薦)", "手動輸入 Token"],
        help="OAuth 登入更方便，會自動取得長期 Token"
    )

    if auth_method == "OAuth 登入 (推薦)":
        # 從配置取得 OAuth 設定
        meta_config = get_meta_oauth_config()  # 你需要實作這個函數

        show_oauth_login_ui(
            app_id=meta_config['app_id'],
            app_secret=meta_config['app_secret'],
            redirect_uri=meta_config['redirect_uri']
        )

        # 檢查是否已認證
        if is_oauth_authenticated():
            st.success("✅ OAuth 認證成功")
            meta_configured = True
            oauth_token = get_oauth_token()
        else:
            meta_configured = False

    else:
        # 原本的手動輸入方式
        meta_token = st.text_input("存取權杖", type="password")
        meta_account_id = st.text_input("廣告帳號 ID")
        meta_configured = bool(meta_token and meta_account_id)
```

---

## 🔄 完整的 OAuth 流程

### 流程圖

```
使用者點擊「使用 Meta 登入」
    ↓
生成 authorization URL (含 state 參數)
    ↓
重定向到 Meta 登入頁面
    ↓
使用者在 Meta 授權應用程式
    ↓
Meta 重定向回 redirect_uri?code=xxx&state=yyy
    ↓
驗證 state（CSRF 保護）
    ↓
用 code 換取短期 token (1小時)
    ↓
用短期 token 換取長期 token (60天)
    ↓
驗證 token 並取得使用者資訊
    ↓
保存到 st.session_state
    ↓
完成！開始使用 API
```

### 程式碼流程

```python
# 1. 初始化 OAuth
oauth = MetaOAuth(app_id, app_secret, redirect_uri)

# 2. 生成授權 URL
auth_url, state = oauth.get_authorization_url()
# 保存 state 到 session
st.session_state.oauth_state = state

# 3. 使用者點擊連結授權
# <a href="{auth_url}">使用 Meta 登入</a>

# 4. 使用者授權後返回，URL 包含 code 參數
code = st.query_params['code']
state_from_url = st.query_params['state']

# 5. 驗證 state
if state_from_url == st.session_state.oauth_state:
    # 6. 換取短期 token
    short_token = oauth.exchange_code_for_token(code)

    # 7. 換取長期 token
    long_token = oauth.exchange_for_long_lived_token(short_token)

    # 8. 保存到 session
    st.session_state.meta_oauth_token = long_token
```

---

## 🛡️ 安全性考量

### CSRF 保護

OAuth 使用 `state` 參數防止 CSRF 攻擊：

```python
# 生成隨機 state
state = secrets.token_urlsafe(32)

# 保存到 session
st.session_state.oauth_state = state

# 授權返回後驗證
if state_from_url != st.session_state.oauth_state:
    raise SecurityError("State 不匹配")
```

### Token 保護

- ✅ Token 存在 `st.session_state`（記憶體中）
- ✅ 不寫入檔案系統
- ✅ 不記錄在日誌中
- ⚠️ 每個使用者 session 獨立

### Redirect URI 驗證

Meta 會驗證 redirect_uri 是否在白名單中：

```python
# 必須完全匹配（包含協議、域名、端口）
META_OAUTH_REDIRECT_URI=http://localhost:8501  ✅
META_OAUTH_REDIRECT_URI=http://localhost:8501/ ❌（多了斜線）
```

---

## 🐛 常見問題

### Q1: redirect_uri_mismatch 錯誤

**錯誤訊息**：
```
Can't Load URL: The domain of this URL isn't included in the app's domains
```

**解決方案**：
1. 確認 Meta 應用程式設定中的 OAuth Redirect URI **完全匹配**
2. 檢查是否包含協議（http/https）
3. 檢查端口號是否正確
4. 不要有多餘的斜線

### Q2: invalid_scope 錯誤

**原因**：請求的權限未被授權

**解決方案**：
1. 前往 Meta 開發者平台
2. 「應用程式審查」→「權限和功能」
3. 確認 `ads_read` 等權限已啟用

### Q3: code 已使用或過期

**原因**：authorization code 只能使用一次

**解決方案**：
1. 清除 URL 參數：`st.query_params.clear()`
2. 重新發起授權流程

### Q4: 本地開發可用，部署後失效

**原因**：Redirect URI 不同

**解決方案**：
1. 在 Meta 應用程式中同時新增兩個 URI：
   - `http://localhost:8501` (開發)
   - `https://your-app.streamlit.app` (生產)

2. 在程式中根據環境自動選擇：
   ```python
   import os

   if os.getenv('ENVIRONMENT') == 'production':
       redirect_uri = "https://your-app.streamlit.app"
   else:
       redirect_uri = "http://localhost:8501"
   ```

---

## 📊 與原有方式的比較

| 特性 | 手動輸入 Token | OAuth 2.0 |
|-----|--------------|-----------|
| 使用者體驗 | ❌ 複雜 | ✅ 簡單 |
| Token 取得 | ❌ 需手動複製貼上 | ✅ 自動 |
| 安全性 | ⚠️ 中等 | ✅ 高 |
| Token 有效期 | 60 天 | 60 天 |
| 初次設定 | ✅ 簡單 | ⚠️ 需設定 OAuth |
| 適用場景 | 開發/測試 | 生產環境 |

---

## 🎯 建議使用情境

### 使用 OAuth（推薦）：
- ✅ 生產環境部署
- ✅ 多使用者應用
- ✅ 需要更好的使用者體驗
- ✅ 企業級應用

### 使用手動輸入：
- ✅ 本地開發測試
- ✅ 單人使用
- ✅ 快速原型開發
- ✅ 不想設定 OAuth

---

## 📚 相關資源

- [Meta OAuth 文件](https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow)
- [Meta App Dashboard](https://developers.facebook.com/apps/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [Streamlit Query Params](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params)

---

**更新日期**：2025-09-30
**適用版本**：v2.0+