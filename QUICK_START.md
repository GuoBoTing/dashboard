# 🚀 快速啟動指南 - OAuth 登入

## ✅ 已完成設定

你的專案已經完成以下設定：

1. ✅ OAuth 2.0 完整實現
2. ✅ 環境變數已配置（.env）
3. ✅ app.py 已整合 OAuth 按鈕
4. ✅ 所有必要的 API 金鑰已填寫

## 🔐 Meta OAuth 設定步驟

### 1. 在 Meta 開發者平台設定 OAuth

前往：https://developers.facebook.com/apps/

1. 選擇你的應用程式（App ID: `2289820758095835`）
2. 左側選單找到「Facebook 登入」→「設定」
3. 在「有效的 OAuth 重新導向 URI」欄位中新增：
   ```
   http://localhost:8501
   ```
4. 點擊「儲存變更」

### 2. 啟動應用程式

```bash
# 確保在專案根目錄
cd "/Users/guobaiting/Desktop/嗜酒食 flambé/flambe-streamlit /flambe-dashboard"

# 啟動 Streamlit
streamlit run app.py
```

### 3. 使用 OAuth 登入

1. 開啟瀏覽器 http://localhost:8501
2. 在側邊欄選擇「**OAuth 登入 (推薦)**」
3. 點擊藍色的「🔐 使用 Meta 登入」按鈕
4. 在 Meta 頁面登入並授權
5. 自動返回應用程式，完成！

## 📊 三種認證方式

你的應用程式現在支援三種 Meta API 認證方式：

### 方式 1：OAuth 登入（推薦）⭐

- **優點**：最簡單，一鍵登入
- **流程**：點擊按鈕 → Meta 授權 → 自動取得 Token
- **有效期**：60 天（自動刷新）

### 方式 2：Token 管理

- **優點**：手動控制 Token
- **流程**：在 UI 輸入短期 token → 系統換取長期 token
- **適用**：開發測試

### 方式 3：基本模式

- **優點**：快速測試
- **流程**：直接在 secrets.toml 設定
- **適用**：單人使用

## 🎯 當前配置

你的 `.env` 檔案已包含：

```bash
META_APP_ID=2289820758095835
META_APP_SECRET=4b5d608fdca56c233c407ca8670abd38
META_ACCOUNT_ID=act_1498662443862674
META_OAUTH_REDIRECT_URI=http://localhost:8501

WC_URL=https://flambe.com.tw
WC_CONSUMER_KEY=ck_ef3d16c67d793dad0221d841410afcfe1649055f
WC_CONSUMER_SECRET=cs_df0e8cdf60fbc6964fdf899e64d6ce2b42766145
```

## 🔍 驗證設定

### 測試 OAuth 功能

```bash
# 執行獨立的 OAuth 測試應用
streamlit run scripts/oauth_example.py
```

### 檢查 Meta 開發者平台

前往：https://developers.facebook.com/apps/2289820758095835/settings/basic/

確認：
- ✅ App ID 正確
- ✅ App Secret 存在
- ✅ 應用程式狀態為「開發中」或「上線」

前往：https://developers.facebook.com/apps/2289820758095835/fb-login/settings/

確認：
- ✅ OAuth Redirect URI 包含 `http://localhost:8501`

## 🐛 常見問題

### Q1: 點擊登入按鈕後顯示 "redirect_uri_mismatch"

**解決方案**：
1. 確認 Meta 應用程式設定中的 OAuth Redirect URI 是 `http://localhost:8501`（不能有斜線）
2. 確認 .env 中的 `META_OAUTH_REDIRECT_URI=http://localhost:8501`
3. 重啟 Streamlit 應用

### Q2: 登入後顯示 "invalid_scope"

**解決方案**：
1. 前往 Meta 開發者平台
2. 「應用程式審查」→「權限和功能」
3. 確認 `ads_read` 權限已啟用

### Q3: 找不到 OAuth 登入選項

**解決方案**：
1. 確認在側邊欄選擇了「OAuth 登入 (推薦)」
2. 如果沒有此選項，檢查 `SECURE_MODE` 是否為 True
3. 確認 src/ 目錄下的模組可以正確導入

## 📚 相關文件

- **[docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)** - 完整的 OAuth 設定指南
- **[docs/META_TOKEN_SETUP.md](docs/META_TOKEN_SETUP.md)** - Token 管理說明
- **[REFACTOR_GUIDE.md](REFACTOR_GUIDE.md)** - 專案重構指南
- **[NEW_STRUCTURE.md](NEW_STRUCTURE.md)** - 專案結構總覽

## 🎉 下一步

OAuth 登入成功後：

1. ✅ Token 自動保存在 session state
2. ✅ 選擇分析期間
3. ✅ 查看儀表板數據
4. ✅ Token 會在剩餘 7 天時自動刷新

享受你的電商分析儀表板！🎊

---

**建立日期**：2025-09-30
**版本**：v2.0 (OAuth 整合版)