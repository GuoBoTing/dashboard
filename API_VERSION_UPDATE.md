# Meta Graph API 版本更新說明

## 📋 更新摘要

**更新日期**: 2025-09-30
**舊版本**: v21.0
**新版本**: v23.0

## ✅ 已更新的文件

### 核心模組
- ✅ `src/constants.py` - META_API_VERSION 常數
- ✅ `src/api/meta_oauth.py` - OAuth 認證 URL
- ✅ `src/api/meta_ads.py` - Meta Ads API 客戶端

### 應用程式
- ✅ `app.py` - 主要應用程式入口

### 腳本工具
- ✅ `scripts/oauth_example.py` - OAuth 範例
- ✅ `scripts/meta_debug.py` - Meta API 調試工具

### 文檔
- ✅ `docs/META_TOKEN_SETUP.md` - Token 設定指南

## 🔗 受影響的 API Endpoints

以下 endpoints 已更新到 v23.0：

1. **OAuth 授權**
   - `https://www.facebook.com/v23.0/dialog/oauth`

2. **Token 交換**
   - `https://graph.facebook.com/v23.0/oauth/access_token`

3. **帳號資訊**
   - `https://graph.facebook.com/v23.0/{account_id}`

4. **廣告數據**
   - `https://graph.facebook.com/v23.0/{account_id}/insights`

5. **用戶資訊**
   - `https://graph.facebook.com/v23.0/me`

## 📚 參考文件

根據 Facebook 官方文件更新：
- [Facebook Login Manual Flow](https://developers.facebook.com/docs/facebook-login/guides/advanced/manual-flow?locale=zh_TW)
- [Graph API Changelog](https://developers.facebook.com/docs/graph-api/changelog)

## 🔄 版本相容性

Meta Graph API 版本說明：
- **v23.0**: 當前最新穩定版本
- **v21.0**: 舊版本（仍在支援期內）
- **向下相容**: v23.0 API 向下相容 v21.0 的主要功能

## ⚠️ 注意事項

1. **確保在 Meta 開發者平台設定中使用相同的 API 版本**
2. **OAuth Redirect URI 必須與應用程式設定匹配**
3. **定期檢查 Meta 的版本更新公告**
4. **建議每 6-12 個月檢查並更新到最新穩定版本**

## 🧪 測試建議

更新後建議執行以下測試：

```bash
# 1. 測試 OAuth 流程
streamlit run scripts/oauth_example.py

# 2. 測試 Meta API 連接
python scripts/meta_debug.py

# 3. 運行完整應用
streamlit run app.py
```

## 📞 相關連結

- [Meta for Developers](https://developers.facebook.com/)
- [Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- [Marketing API](https://developers.facebook.com/docs/marketing-apis/)