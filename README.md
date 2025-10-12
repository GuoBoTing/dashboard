# 📊 Flambé Dashboard - 電商業績分析儀表板

> 整合 WooCommerce 與 Meta 廣告數據的專業電商分析平台

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 專案簡介

Flambé Dashboard 是一個基於 Streamlit 開發的電商業績分析儀表板，專為需要整合多個數據源並進行深度財務分析的電商企業設計。

### ✨ 核心功能

- **📈 即時數據整合**：自動整合 WooCommerce 訂單數據與 Meta 廣告數據
- **💰 全面成本分析**：計算進貨成本、運費、金流手續費、廣告費、營業稅
- **📊 視覺化報表**：使用 Plotly 生成互動式圖表與趨勢分析
- **🔒 安全配置管理**：支援 Streamlit Secrets 加密存儲 API 金鑰
- **🔄 自動 Token 刷新**：Meta API Long-lived Token 自動續期
- **💾 數據匯出**：支援 CSV 格式的詳細分析報告下載
- **🔍 調試模式**：內建詳細的 API 請求與響應日誌功能

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- pip 或 conda 套件管理器

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd flambe-dashboard
   ```

2. **建立虛擬環境（建議）**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置環境變數**

   建立 `.env` 檔案（本地開發）：
   ```bash
   nano .env
   ```

   填入以下內容：
   ```bash
   # Meta API 設定
   META_APP_ID=123456789
   META_APP_SECRET=abcdef123456
   META_ACCOUNT_ID=act_123456789
   META_LONG_LIVED_TOKEN=    # 可選，可透過 UI 生成

   # WooCommerce API 設定
   WC_URL=https://your-store.com
   WC_CONSUMER_KEY=ck_xxxxxxxxxxxxx
   WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxx
   ```

   > 💡 **Token 管理方式**：
   > - **本地開發**：在 UI 的「Token 管理」區塊輸入短期 token，系統會自動轉換為長期 token 並儲存
   > - **Zeabur 部署**：將長期 token 設定到環境變數 `META_LONG_LIVED_TOKEN`，系統會自動載入
   >
   > 詳細設定請參考：[TOKEN_管理指南.md](TOKEN_管理指南.md) 和 [ZEABUR_部署指南.md](ZEABUR_部署指南.md)

5. **啟動儀表板**
   ```bash
   streamlit run app.py
   ```

   瀏覽器會自動開啟 `http://localhost:8501`

## 📖 使用說明

### 基本操作流程

1. **設定 API 連接**
   - 在側邊欄確認 WooCommerce 和 Meta 廣告的連接狀態
   - 如果使用基本模式，需手動輸入 API 金鑰

2. **選擇分析期間**
   - 在側邊欄的「分析期間」選擇日期範圍
   - 系統會自動調整到昨天（避免 Meta API 數據延遲）

3. **調整成本參數**
   - 使用「成本設定」滑桿調整進貨成本率（預設 50%）
   - 系統會自動計算運費、金流手續費等其他成本

4. **查看分析結果**
   - **營運總覽**：總營收、訂單數、客單價、估計淨利
   - **成本分析**：五大成本類別的詳細分析
   - **廣告數據**：曝光、點擊、CTR、ROAS 等指標
   - **趨勢分析**：每日營收、廣告支出、ROAS 趨勢圖

5. **匯出數據**
   - 使用「數據匯出」區塊下載 CSV 格式報告
   - 可匯出：每日數據、付款分析、運送分析、成本分析

### 調試模式

如果遇到 Meta API 問題（例如廣告費顯示為零）：

1. 在側邊欄勾選「啟用調試模式」
2. 查看詳細的 API 請求與響應信息
3. 或使用獨立調試工具：
   ```bash
   python meta_debug.py
   ```
   （需先在檔案中設定 `ACCESS_TOKEN` 和 `ACCOUNT_ID`）

詳細的故障排除指南請參考：[META_API_修復指南.md](META_API_修復指南.md)

## 🏗️ 專案架構

```
flambe-dashboard/
├── app.py                      # 主程式入口 ⭐
├── config.py                   # 配置管理模組
├── requirements.txt            # Python 依賴清單
├── .gitignore                  # Git 忽略規則
├── .env                        # 環境變數（不提交到 Git）
│
├── src/api/
│   ├── meta_token_manager.py  # Meta Token 自動管理模組 🆕
│   └── woocommerce.py          # WooCommerce API 客戶端
│
├── test_1007.py                # 10/7 特定日期訂單測試
├── test_wc_orders.py           # WooCommerce 訂單狀態測試
│
├── CLAUDE.md                   # Claude Code 開發指南
├── README.md                   # 專案說明（本檔案）
├── TOKEN_管理指南.md           # Token 管理完整說明 🆕
├── ZEABUR_部署指南.md          # Zeabur 部署步驟 🆕
├── CURRENT_STRUCTURE.md        # 當前結構分析
├── PROJECT_STRUCTURE.md        # 重組計劃
└── META_API_修復指南.md        # Meta API 故障排除
```

詳細的架構說明請參考：[CLAUDE.md](CLAUDE.md)

## 💡 核心技術

- **[Streamlit](https://streamlit.io/)** - Web 應用框架
- **[Pandas](https://pandas.pydata.org/)** - 數據處理與分析
- **[Plotly](https://plotly.com/python/)** - 互動式數據視覺化
- **[Requests](https://requests.readthedocs.io/)** - HTTP API 請求
- **WooCommerce REST API** - 電商訂單數據
- **Meta Graph API** - 廣告數據與洞察

## 📊 數據指標說明

### 成本計算邏輯

儀表板會自動計算以下成本：

| 成本類型 | 計算方式 | 說明 |
|---------|---------|------|
| **進貨成本 (COGS)** | 營收 × 成本率 | 可透過滑桿調整（20%-80%）|
| **運費** | 每日訂單實際運費累加 | 根據每筆訂單的運送方式計算（宅配/超商/郵寄） |
| **金流手續費** | 每日訂單實際手續費累加 | 根據每筆訂單的付款方式和金額計算 |
| **廣告費** | Meta API 直接取得 | 實際廣告支出 |
| **營業稅** | 營收 × 5% | 固定稅率 |

**淨利計算公式**：
```
淨利 = 營收 - (進貨成本 + 運費 + 金流手續費 + 廣告費 + 營業稅)
```

> ⚠️ **重要更新（2025-10-12）**：
> - 運費和金流手續費已改為**按實際訂單計算**，而非按日平均分配
> - 每日成本 = 當日所有訂單的實際運費/手續費總和
> - 無訂單的日期成本為 0，避免虛假成本分配

### 運費與手續費設定

可在 `app.py` 中修改費率：

- **運費設定** (第 92 行)：`SHIPPING_COSTS` 字典
- **金流手續費** (第 96 行)：`PAYMENT_FEES` 字典
- **營業稅率** (第 101 行)：`TAX_RATE` 常數

## 🔐 安全性說明

- ⚠️ **絕對不要**將 `.streamlit/secrets.toml` 或 `.env` 提交到 Git
- ✅ 已包含在 `.gitignore` 中
- ✅ 在 Streamlit Cloud 部署時，請在設定中配置 Secrets
- ✅ Meta Token 支援自動刷新，無需頻繁手動更新

## 🐛 常見問題

### Q1: Meta 廣告費顯示為 $0？

**可能原因**：
- Meta API 數據有 1-2 天延遲
- Token 過期或權限不足
- 查詢了當天或未來的日期

**解決方案**：
1. 啟用「調試模式」查看 API 響應
2. 確認日期範圍不包含今天
3. 參考 [META_API_修復指南.md](META_API_修復指南.md)

### Q2: WooCommerce API 連接失敗？

**檢查清單**：
- 確認商店網址格式正確（https://your-store.com）
- 檢查 Consumer Key 和 Secret 是否正確
- 確認 API 權限包含「讀取訂單」

### Q3: 如何部署到 Streamlit Cloud？

1. 將專案推送到 GitHub
2. 連接 [Streamlit Cloud](https://streamlit.io/cloud)
3. 在部署設定中添加 Secrets（與 `secrets.toml` 相同格式）
4. 部署 `app.py`

## 📝 開發文件

- **[CLAUDE.md](CLAUDE.md)** - 開發者指南與架構說明
- **[TOKEN_管理指南.md](TOKEN_管理指南.md)** - Meta Token 管理完整說明
- **[ZEABUR_部署指南.md](ZEABUR_部署指南.md)** - Zeabur 雲端部署步驟
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 專案重構計劃
- **[CURRENT_STRUCTURE.md](CURRENT_STRUCTURE.md)** - 當前結構分析
- **[META_API_修復指南.md](META_API_修復指南.md)** - API 故障排除

## 🔧 測試工具

專案包含以下測試腳本：

- **test_1007.py** - 測試特定日期（10/7）的訂單資料，用於驗證自訂訂單狀態
- **test_wc_orders.py** - 測試不同訂單狀態組合的資料抓取，確認營收計算準確性

執行測試：
```bash
source venv/bin/activate
python test_1007.py          # 測試特定日期
python test_wc_orders.py     # 測試訂單狀態
```

## 🆕 最近更新

### v2.1 (2025-10-12)
- ✅ 修正運費和金流手續費計算方式為按實際訂單計算
- ✅ 支援 WooCommerce 自訂訂單狀態（wmp-in-transit, wmp-shipped, ry-at-cvs）
- ✅ 新增 Token 自動管理系統，支援本地和雲端部署
- ✅ 新增 Zeabur 部署支援和環境變數配置

### v2.0 (2025-09-30)
- ✅ 整合 WooCommerce 和 Meta Ads 數據
- ✅ 實現自動 Token 刷新機制
- ✅ 新增成本分析和淨利計算功能

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

本專案採用 MIT 授權條款。

## 📧 聯絡方式

如有問題或建議，請透過 GitHub Issues 聯繫。

---

**最後更新**：2025-10-12
**版本**：v2.1
**維護狀態**：✅ 活躍維護中
