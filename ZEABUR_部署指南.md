# 🚀 Zeabur 部署指南 - Meta Token 管理

> 針對 Zeabur 雲端平台的 Token 持久化方案

## 📋 目錄

- [部署策略](#部署策略)
- [方案 A：環境變數（推薦）](#方案-a環境變數推薦)
- [方案 B：Session State（臨時）](#方案-b-session-state臨時)
- [完整部署流程](#完整部署流程)
- [常見問題](#常見問題)

---

## 🎯 部署策略

### Zeabur 的特性

✅ **優點**：
- 自動部署 Git 倉庫
- 支援環境變數設定
- 自動 HTTPS 憑證

⚠️ **限制**：
- **容器重啟時，本地檔案會消失**
- Session State 僅在使用者會話期間有效

### 我們的解決方案

系統會**自動偵測**執行環境，並採用最佳儲存策略：

| 環境 | 儲存模式 | 持久化 | 說明 |
|------|---------|--------|------|
| 本地開發 | 📁 File | ✅ | 儲存到 `.streamlit/meta_token.json` |
| Zeabur | 🔄 Session | ❌ | 重啟後需重新設定 |
| Zeabur + 環境變數 | 🔒 Env Var | ✅ | **推薦方案** |

---

## 方案 A：環境變數（推薦）

### 🌟 優點

- ✅ **持久化**：服務重啟後 Token 不會消失
- ✅ **安全**：不會暴露在程式碼中
- ✅ **簡單**：一次設定，永久有效

### 📝 設定步驟

#### 步驟 1：在本地取得長期 Token

1. 在本地執行應用程式：
   ```bash
   streamlit run app.py
   ```

2. 在側邊欄「Meta Token 管理」區塊：
   - 貼上短期 Token
   - 點擊「🔄 轉換為長期 Token」

3. 展開「🔍 查看 Token 資訊」
4. 複製顯示的完整 Token（以 `EAA` 開頭的長字串）

#### 步驟 2：在 Zeabur 設定環境變數

1. 登入 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 選擇你的專案
3. 點擊你的服務（flambe-dashboard）
4. 進入「Variables」（變數）頁籤
5. 新增環境變數：

   ```bash
   # 變數名稱
   META_LONG_LIVED_TOKEN

   # 變數值（貼上你的長期 Token）
   EAAh2H7ZC8zw0BO...（你的完整 Token）
   ```

6. 點擊「Save」儲存

#### 步驟 3：重新部署

環境變數更新後，Zeabur 會自動重新部署服務。

#### 步驟 4：驗證

1. 訪問你的 Zeabur 網址：`https://flambe-dashboard.zeabur.app`
2. 側邊欄應該顯示：
   ```
   ✅ Token 已設定且有效
   🔒 儲存模式: Session State（雲端部署）
   ```
3. 系統會自動從環境變數載入 Token

### 🔄 Token 更新流程

當 Token 即將過期時：

1. 在應用程式中點擊「🔄 手動更新 Token」
2. 系統會自動刷新 Token
3. 複製新的 Token
4. 更新 Zeabur 環境變數 `META_LONG_LIVED_TOKEN`
5. 重新部署

---

## 方案 B：Session State（臨時）

### ⚠️ 限制

- ❌ **不持久**：服務重啟後 Token 會消失
- ❌ **需重新設定**：每次重啟都要重新輸入 Token

### 📝 使用場景

適合：
- 🧪 測試部署
- 🔍 臨時查看數據
- 🚀 快速驗證功能

### 操作步驟

1. 訪問 Zeabur 網址
2. 在側邊欄輸入短期 Token
3. 系統轉換為長期 Token 並儲存到 Session
4. **注意**：服務重啟後需要重複此步驟

---

## 完整部署流程

### 初次部署

#### 1️⃣ 準備環境變數

在 Zeabur 設定以下環境變數：

```bash
# WooCommerce 設定
WC_URL=https://flambe.com.tw
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxx

# Meta 基本設定
META_APP_ID=2289820758095835
META_APP_SECRET=4b5d608fdca56c233c407ca8670abd38
META_ACCOUNT_ID=act_1498662443862674

# Meta Token（可選，稍後設定）
META_LONG_LIVED_TOKEN=（暫時留空）
```

#### 2️⃣ 部署應用程式

1. 連接 GitHub 倉庫
2. Zeabur 自動偵測為 Python 專案
3. 等待部署完成

#### 3️⃣ 設定 Meta Token

**方式 A：在本地取得後設定到環境變數**（推薦）
- 參考上方「方案 A」步驟

**方式 B：直接在 Zeabur 應用程式中設定**
- 訪問應用程式 → 輸入短期 Token → 轉換
- 注意：重啟後需重新設定

### 更新部署

#### 更新程式碼
```bash
git add .
git commit -m "更新功能"
git push
```
Zeabur 會自動重新部署

#### 更新 Token
1. 在應用程式中手動更新 Token
2. 複製新 Token
3. 更新 Zeabur 環境變數
4. 重新部署（或等待自動部署）

---

## 🔍 故障排除

### ❌ Token 在重啟後消失

**原因**：未設定環境變數 `META_LONG_LIVED_TOKEN`

**解決方案**：
1. 參考「方案 A」設定環境變數
2. 或接受每次重啟都要重新輸入 Token（方案 B）

### ❌ 環境變數設定後無效

**可能原因**：
1. 環境變數名稱錯誤（必須是 `META_LONG_LIVED_TOKEN`）
2. 未重新部署服務

**解決方案**：
1. 檢查變數名稱拼寫
2. 手動觸發重新部署：
   - Zeabur Dashboard → 服務 → 右上角 ⋮ → Redeploy

### ❌ Token 自動更新失敗

**原因**：Token 已完全過期

**解決方案**：
1. 重新從 Meta Graph API Explorer 取得短期 Token
2. 在應用程式中轉換為長期 Token
3. 更新環境變數

---

## 💡 最佳實踐

### ✅ 推薦做法

1. **使用環境變數儲存長期 Token**
   - 持久化，不怕重啟
   - 安全，不會外洩

2. **定期監控 Token 狀態**
   - 在應用程式中查看「剩餘天數」
   - 剩餘 < 10 天時手動更新

3. **備份 Token**
   - 將 Token 儲存在密碼管理器
   - 或記錄在安全的地方

4. **測試環境分離**
   - 開發、生產使用不同的 Token
   - 避免測試影響正式數據

### ❌ 避免做法

1. ❌ 將 Token 寫入程式碼
2. ❌ 將 Token 提交到 Git
3. ❌ 在公開場合分享 Token
4. ❌ 忽略 Token 過期警告

---

## 📊 儲存模式對比

| 模式 | 本地開發 | Zeabur 部署 | 持久化 | 設定難度 |
|------|---------|-------------|--------|---------|
| **File** | ✅ 推薦 | ❌ 不適用 | ✅ | ⭐ 簡單 |
| **Session** | ⚠️ 可用 | ⚠️ 臨時方案 | ❌ | ⭐ 簡單 |
| **Env Var** | ✅ 可用 | ✅ 推薦 | ✅ | ⭐⭐ 中等 |

---

## 🎯 快速參考

### 環境變數清單

```bash
# 必填
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxx
WC_CONSUMER_SECRET=cs_xxxxx
META_APP_ID=xxxxx
META_APP_SECRET=xxxxx
META_ACCOUNT_ID=act_xxxxx

# 選填（推薦設定以持久化 Token）
META_LONG_LIVED_TOKEN=EAAxxxxx
```

### Token 取得流程

```
1. Meta Graph API Explorer
   ↓ 產生短期 Token
2. 應用程式 UI
   ↓ 轉換為長期 Token
3. 複製 Token
   ↓
4. Zeabur 環境變數
   ↓ 設定 META_LONG_LIVED_TOKEN
5. 完成！✅
```

---

## 📞 需要協助？

- 📖 查看 [TOKEN_管理指南.md](TOKEN_管理指南.md)
- 🐛 回報問題：GitHub Issues
- 📧 技術支援：透過 Issues 聯繫

---

**最後更新**：2025-10-08
**版本**：v3.1（Zeabur 雲端部署版）
**維護狀態**：✅ 活躍維護中
