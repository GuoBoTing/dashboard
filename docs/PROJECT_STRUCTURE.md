# 專案結構重組計劃

## 📊 建議的新結構

```
flambe-dashboard/
│
├── app.py                          # 主程式入口（保持在根目錄）
├── requirements.txt                # 依賴套件清單
├── README.md                       # 專案說明文件
├── CLAUDE.md                       # Claude Code 開發指南
│
├── .streamlit/                     # Streamlit 配置目錄
│   ├── config.toml                 # Streamlit 設定
│   └── secrets.toml                # API 金鑰（不提交到 Git）
│
├── src/                            # 核心程式碼
│   ├── __init__.py
│   ├── config.py                   # 配置管理模組
│   │
│   ├── api/                        # API 客戶端模組
│   │   ├── __init__.py
│   │   ├── woocommerce.py          # WooCommerce API 客戶端
│   │   ├── meta_ads.py             # Meta Ads API 客戶端（從 meta_api_enhanced.py 重構）
│   │   └── meta_token_manager.py   # Meta Token 管理
│   │
│   ├── utils/                      # 工具函數
│   │   ├── __init__.py
│   │   ├── cost_calculator.py      # 成本計算（運費、手續費等）
│   │   ├── data_processor.py       # 數據處理與轉換
│   │   └── validators.py           # 資料驗證
│   │
│   ├── ui/                         # UI 組件
│   │   ├── __init__.py
│   │   ├── sidebar.py              # 側邊欄組件
│   │   ├── metrics.py              # 指標卡片
│   │   ├── charts.py               # 圖表組件
│   │   └── styles.py               # CSS 樣式
│   │
│   └── constants.py                # 常數定義（運費、手續費等）
│
├── pages/                          # Streamlit 多頁面應用（可選）
│   ├── 1_📊_Dashboard.py           # 主儀表板
│   ├── 2_💰_Cost_Analysis.py       # 成本分析
│   ├── 3_📈_Trends.py              # 趨勢分析
│   └── 4_⚙️_Settings.py            # 設定頁面
│
├── scripts/                        # 獨立腳本工具
│   ├── meta_debug.py               # Meta API 調試工具
│   ├── meta_api_test.py            # Meta API 測試
│   └── data_export.py              # 數據匯出工具
│
├── tests/                          # 測試檔案
│   ├── __init__.py
│   ├── test_api.py                 # API 測試
│   ├── test_cost_calculator.py     # 成本計算測試
│   └── test_data_processor.py      # 數據處理測試
│
├── docs/                           # 文件資料夾
│   ├── META_API_修復指南.md
│   ├── DEPLOYMENT.md               # 部署指南
│   └── API_REFERENCE.md            # API 參考文件
│
├── data/                           # 數據檔案（可選）
│   ├── .gitkeep
│   └── exports/                    # 匯出的 CSV 檔案
│
└── .gitignore                      # Git 忽略清單
```

## 🔄 重構步驟

### 階段 1：建立目錄結構
1. 建立 `src/`, `src/api/`, `src/utils/`, `src/ui/` 目錄
2. 建立 `scripts/`, `docs/`, `tests/` 目錄
3. 建立所有 `__init__.py` 檔案

### 階段 2：分離核心功能模組
1. **config.py** → 保持在 `src/config.py`
2. **meta_api_enhanced.py** → 拆分為：
   - `src/api/meta_ads.py` (MetaAdsAPI 類)
   - `src/api/meta_token_manager.py` (Token 管理)
3. **app.py** → 拆分為：
   - 保留主程式在 `app.py`
   - WooCommerce 函數 → `src/api/woocommerce.py`
   - 成本計算函數 → `src/utils/cost_calculator.py`
   - UI 組件 → `src/ui/` 各模組
   - 常數 → `src/constants.py`

### 階段 3：移動工具與文件
1. **meta_debug.py** → `scripts/meta_debug.py`
2. **meta_api_test.py** → `scripts/meta_api_test.py`
3. **META_API_修復指南.md** → `docs/META_API_修復指南.md`
4. **instructure.md** → 刪除（內容整合到 README.md）

### 階段 4：更新主程式
1. 更新 `app.py` 的 import 路徑
2. 簡化主程式邏輯，使用模組化的函數

### 階段 5：處理重複檔案
1. 比較 `app.py` 和 `dashboard.py`
2. 保留較新或功能完整的版本
3. 將舊版移到 `archive/` 或刪除

## 📝 建議的 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# Data
data/exports/*.csv
*.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

## 🎯 重構後的優勢

1. ✅ **清晰的模組化結構**：每個功能都有明確的位置
2. ✅ **易於維護**：相關程式碼集中管理
3. ✅ **可測試性**：獨立模組易於單元測試
4. ✅ **可擴展性**：新增功能時不會讓根目錄更混亂
5. ✅ **協作友善**：團隊成員容易找到對應的程式碼
6. ✅ **部署簡單**：主程式 `app.py` 保持在根目錄，符合 Streamlit Cloud 要求

## 📌 重要提醒

- 主程式 `app.py` 必須保持在根目錄（Streamlit Cloud 部署要求）
- `.streamlit/secrets.toml` 絕對不能提交到 Git
- 重構時保持一個可運行的版本，避免完全停擺
- 建議使用 Git 分支進行重構，測試無誤後再合併

## 🚀 快速開始（重構後）

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定 Secrets（首次使用）
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 編輯 secrets.toml 填入 API 金鑰

# 執行主程式
streamlit run app.py

# 執行調試工具
python scripts/meta_debug.py

# 執行測試
pytest tests/
```