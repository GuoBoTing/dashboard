# Meta API Token 設定指南

## 🔑 Token 類型說明

Meta API 有三種 Token 類型：

| Token 類型 | 有效期 | 用途 | 是否應存在 .env |
|-----------|-------|------|----------------|
| **短期 Token** | 1-2 小時 | 臨時測試、換取長期 Token | ❌ 不要 |
| **長期 Token** | ~60 天 | 正常使用 | ✅ 可選 |
| **永久 Token** | 永久 | 系統用戶（需審核） | ✅ 可以 |

## 🚀 首次設定流程

### 方法 1：透過 Streamlit UI 設定（推薦）

1. **在 `.env` 或 `.streamlit/secrets.toml` 中設定基本資訊**：
   ```toml
   META_APP_ID=your_app_id
   META_APP_SECRET=your_app_secret
   META_ACCOUNT_ID=act_123456789
   META_LONG_LIVED_TOKEN=  # 留空
   ```

2. **啟動 Streamlit 應用**：
   ```bash
   streamlit run app.py
   ```

3. **取得短期 Token**：
   - 前往 [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - 選擇你的應用程式
   - 選擇權限：`ads_read`, `ads_management`
   - 點擊「生成存取權杖」
   - 複製產生的短期 token（有效期 1-2 小時）

4. **在 UI 中生成長期 Token**：
   - 在側邊欄找到「🔑 Token 管理」
   - 展開「初始化長期 Token」
   - 貼上短期 token
   - 點擊「生成長期 Token」
   - ✅ 系統會自動將長期 token 存入 session state

5. **完成**！
   - 長期 token 有效期約 60 天
   - 系統會在剩餘 7 天時自動刷新
   - 不需要手動更新

### 方法 2：手動換取長期 Token

如果你想手動換取並保存長期 token：

```bash
# 使用 curl 換取長期 token
curl -X GET "https://graph.facebook.com/v23.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

回應範例：
```json
{
  "access_token": "EAABsb...(長期token)",
  "token_type": "bearer",
  "expires_in": 5183944  // 約 60 天
}
```

然後將長期 token 存入 `.streamlit/secrets.toml`：
```toml
[meta]
app_id = "your_app_id"
app_secret = "your_app_secret"
account_id = "act_123456789"
long_lived_token = "EAABsb...(你的長期token)"
```

## 🔄 Token 自動刷新機制

系統已內建自動刷新功能（`meta_api_enhanced.py`）：

### 工作原理

1. **檢查過期時間**：
   - 每次 API 請求前，檢查 token 是否在 7 天內過期
   - 過期資訊存在 `st.session_state.meta_token_info`

2. **自動刷新**：
   ```python
   # 系統自動執行
   if token_expires_in < 7_days:
       new_token = api_client.refresh_long_lived_token()
       # 新 token 自動保存到 session state
   ```

3. **錯誤重試**：
   - 如果 API 返回 401/403 錯誤（token 無效）
   - 自動嘗試刷新 token 並重試請求

### 查看 Token 狀態

在 Streamlit UI 中：
1. 前往側邊欄
2. 展開「🔑 Token 管理」
3. 查看：
   - 當前 Token 狀態（有效/即將過期/已過期）
   - 剩餘天數
   - 到期時間

## 📋 Secrets 設定檔範例

### `.streamlit/secrets.toml`（生產環境推薦）

```toml
[woocommerce]
url = "https://your-store.com"
consumer_key = "ck_xxxxxxxxxxxxx"
consumer_secret = "cs_xxxxxxxxxxxxx"

[meta]
app_id = "123456789"
app_secret = "abcdef123456"
account_id = "act_123456789"
long_lived_token = "EAABsb..."  # 可選，留空則首次使用時在 UI 生成
```

### `.env`（開發環境）

```bash
# Meta API
META_APP_ID=123456789
META_APP_SECRET=abcdef123456
META_ACCOUNT_ID=act_123456789
META_LONG_LIVED_TOKEN=  # 留空，在 UI 中生成

# WooCommerce
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxx
```

## 🔍 除錯與驗證

### 測試 Token 是否有效

使用內建的調試工具：

```bash
python meta_debug.py
```

在檔案中設定：
```python
ACCESS_TOKEN = "你的_token"
ACCOUNT_ID = "act_123456789"
```

工具會自動：
- ✅ 測試帳號存取權限
- ✅ 驗證廣告數據讀取
- ✅ 顯示詳細的錯誤訊息

### 常見錯誤代碼

| 錯誤代碼 | 說明 | 解決方案 |
|---------|------|---------|
| `190` | Token 無效或過期 | 重新生成長期 token |
| `100` | 權限不足 | 檢查 token 權限範圍 |
| `463` | Token 已被撤銷 | 重新生成新 token |
| `1` | 未知錯誤 | 檢查參數格式 |

## 🛡️ 安全最佳實踐

### ✅ 應該做的

1. **使用 Streamlit Secrets**（生產環境）
   - 在 Streamlit Cloud 部署時，在設定中配置 Secrets
   - 不要將 secrets.toml 提交到 Git

2. **定期輪換 App Secret**
   - 每 3-6 個月更換一次
   - 在 Meta 開發者平台重設

3. **限制 Token 權限**
   - 只授予必要的權限（`ads_read`）
   - 避免使用 `ads_management` 除非需要

4. **監控 Token 使用**
   - 在 Meta 開發者平台檢查 API 使用情況
   - 設定異常警報

### ❌ 不應該做的

1. ❌ 不要將 `.env` 或 `secrets.toml` 提交到 Git
2. ❌ 不要在程式碼中寫死 token
3. ❌ 不要在公開場合分享 App Secret
4. ❌ 不要使用短期 token 作為長期解決方案

## 📚 相關資源

- [Meta Graph API 文件](https://developers.facebook.com/docs/graph-api/)
- [存取權杖說明](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/)
- [Meta API Explorer](https://developers.facebook.com/tools/explorer/)
- [Meta 廣告 API](https://developers.facebook.com/docs/marketing-apis/)

## 🆘 需要幫助？

如果遇到 token 相關問題：

1. 啟用儀表板的「調試模式」
2. 查看 [META_API_修復指南.md](META_API_修復指南.md)
3. 執行 `python meta_debug.py` 進行診斷
4. 檢查 Meta 開發者平台的錯誤日誌

---

**更新日期**：2025-09-30
**適用版本**：v2.0+