# 專案重構指南

## ✅ 已完成的重構

### 1. 目錄結構

```
flambe-dashboard/
├── app.py                      # 主程式（需更新以使用新模組）
├── app_backup.py               # 原始備份
├── requirements.txt
├── README.md
├── CLAUDE.md
├── .env
├── .env.example
├── .gitignore
│
├── src/                        # ✅ 核心程式碼
│   ├── __init__.py
│   ├── config.py               # ✅ 配置管理
│   ├── constants.py            # ✅ 常數定義
│   │
│   ├── api/                    # ✅ API 客戶端
│   │   ├── __init__.py
│   │   ├── woocommerce.py      # ✅ WooCommerce API
│   │   ├── meta_ads.py         # ✅ Meta Ads API (原 meta_api_enhanced.py)
│   │   └── meta_oauth.py       # ✅ OAuth 2.0 認證
│   │
│   ├── utils/                  # ✅ 工具函數
│   │   ├── __init__.py
│   │   └── cost_calculator.py  # ✅ 成本計算
│   │
│   └── ui/                     # ✅ UI 組件
│       ├── __init__.py
│       └── styles.py           # ✅ CSS 樣式
│
├── scripts/                    # ✅ 獨立腳本
│   ├── meta_debug.py           # ✅ Meta API 調試工具
│   ├── meta_api_test.py        # ✅ API 測試
│   └── oauth_example.py        # ✅ OAuth 範例
│
├── docs/                       # ✅ 文件
│   ├── META_API_修復指南.md
│   ├── META_TOKEN_SETUP.md
│   ├── OAUTH_SETUP.md
│   ├── CURRENT_STRUCTURE.md
│   └── PROJECT_STRUCTURE.md
│
├── tests/                      # ⚠️ 待建立
│   └── __init__.py
│
└── data/                       # ✅ 數據目錄
    ├── .gitkeep
    └── exports/
```

### 2. 已建立的模組

#### src/constants.py
- ✅ 運費設定 (SHIPPING_COSTS)
- ✅ 金流手續費率 (PAYMENT_FEES)
- ✅ 稅率 (TAX_RATE)
- ✅ 其他常數

#### src/api/woocommerce.py
- ✅ `WooCommerceAPI` 類
- ✅ `get_orders()` - 取得訂單
- ✅ `test_connection()` - 測試連接

#### src/api/meta_ads.py
- ✅ `MetaAdsAPI` 類 (原 meta_api_enhanced.py)
- ✅ Token 刷新功能
- ✅ 自動過期檢測

#### src/api/meta_oauth.py
- ✅ `MetaOAuth` 類
- ✅ OAuth 2.0 完整流程
- ✅ `show_oauth_login_ui()` - UI 組件

#### src/utils/cost_calculator.py
- ✅ `calculate_shipping_costs()` - 運費計算
- ✅ `calculate_payment_fees()` - 手續費計算
- ✅ `calculate_cogs()` - 進貨成本
- ✅ `calculate_business_tax()` - 營業稅
- ✅ `calculate_net_profit()` - 淨利

#### src/ui/styles.py
- ✅ `apply_custom_css()` - 應用樣式
- ✅ `render_main_header()` - 主標題
- ✅ `render_section_header()` - 區塊標題
- ✅ `render_mode_badge()` - 模式徽章

---

## 🔄 如何更新 app.py

### 步驟 1：更新 imports

在 `app.py` 頂部，替換舊的 imports：

```python
# 舊的（刪除）
from config import Config, setup_api_connections, get_active_config
from meta_api_enhanced import get_enhanced_meta_ads_data, show_token_management, MetaAdsAPI

# 新的（加入）
from src.config import Config, setup_api_connections, get_active_config
from src.api.meta_ads import get_enhanced_meta_ads_data, show_token_management, MetaAdsAPI
from src.api.meta_oauth import show_oauth_login_ui, get_oauth_token, is_oauth_authenticated
from src.api.woocommerce import get_woocommerce_data
from src.utils.cost_calculator import (
    calculate_shipping_costs,
    calculate_payment_fees,
    calculate_cogs,
    calculate_business_tax,
    calculate_net_profit,
    calculate_total_costs
)
from src.ui.styles import apply_custom_css, render_main_header, render_mode_badge
from src.constants import (
    SHIPPING_COSTS,
    PAYMENT_FEES,
    TAX_RATE,
    PAGE_TITLE,
    PAGE_ICON
)
```

### 步驟 2：替換常數定義

刪除 app.py 中的常數定義（第 92-101 行）：
```python
# 刪除這些
SHIPPING_COSTS = {...}
PAYMENT_FEES = {...}
TAX_RATE = 0.05
```

### 步驟 3：替換樣式

刪除 app.py 中的 CSS 定義（第 31-89 行），替換為：
```python
# 應用自定義樣式
apply_custom_css()
```

### 步驟 4：更新標題渲染

刪除原本的標題 markdown（第 104-109 行），替換為：
```python
# 主標題
render_main_header(
    title="電商業績分析儀表板",
    subtitle="WooCommerce 與 Meta 廣告整合分析平台"
)
```

### 步驟 5：更新模式顯示

刪除原本的模式顯示（第 112-115 行），替換為：
```python
# 顯示運行模式
if SECURE_MODE:
    render_mode_badge("secure")
elif is_oauth_authenticated():
    render_mode_badge("oauth")
else:
    render_mode_badge("basic")
```

### 步驟 6：加入 OAuth 登入選項

在側邊欄中（第 118 行之後），加入：

```python
with st.sidebar:
    st.header("設定面板")
    st.markdown("---")

    # 選擇認證方式
    auth_method = st.radio(
        "Meta API 認證方式",
        ["OAuth 登入 (推薦)", "手動 Token 管理", "基本模式"],
        help="選擇 Meta API 的認證方式"
    )

    if auth_method == "OAuth 登入 (推薦)":
        # OAuth 登入
        if SECURE_MODE:
            _, meta_config = get_active_config()
            redirect_uri = meta_config.get('oauth_redirect_uri', 'http://localhost:8501')

            show_oauth_login_ui(
                app_id=meta_config['app_id'],
                app_secret=meta_config['app_secret'],
                redirect_uri=redirect_uri
            )

            meta_configured = is_oauth_authenticated()
            if meta_configured:
                oauth_token = get_oauth_token()
        else:
            st.warning("OAuth 需要在 secrets.toml 中設定 app_id 和 app_secret")
            meta_configured = False

    elif auth_method == "手動 Token 管理":
        # 原有的 Token 管理方式
        if SECURE_MODE:
            wc_configured, meta_configured = setup_api_connections()
        # ... 其餘原有代碼

    else:  # 基本模式
        # 手動輸入
        # ... 原有的手動輸入代碼
```

### 步驟 7：刪除計算函數

刪除 app.py 中的這些函數（已移到 src/utils/cost_calculator.py）：
- `calculate_shipping_costs()` (第 164-176 行)
- `calculate_payment_fees()` (第 178-196 行)

### 步驟 8：更新 WooCommerce 數據獲取

替換 `get_enhanced_woocommerce_data()` 呼叫：

```python
# 舊的
orders_df, payment_methods, shipping_methods = get_enhanced_woocommerce_data(
    wc_url, wc_key, wc_secret, start_date, end_date
)

# 新的
from src.api.woocommerce import get_woocommerce_data
orders_df, payment_methods, shipping_methods = get_woocommerce_data(
    wc_url, wc_key, wc_secret, start_date, end_date
)
```

---

## 🚀 快速測試

### 1. 測試新模組是否正常

```bash
# 測試 imports
python3 -c "from src.constants import SHIPPING_COSTS; print('✅ Constants OK')"
python3 -c "from src.api.woocommerce import WooCommerceAPI; print('✅ WooCommerce API OK')"
python3 -c "from src.api.meta_oauth import MetaOAuth; print('✅ OAuth OK')"
python3 -c "from src.utils.cost_calculator import calculate_shipping_costs; print('✅ Cost Calculator OK')"
python3 -c "from src.ui.styles import apply_custom_css; print('✅ UI Styles OK')"
```

### 2. 測試 OAuth 範例

```bash
streamlit run scripts/oauth_example.py
```

### 3. 測試主應用

```bash
streamlit run app.py
```

---

## 📋 待完成項目

### 高優先級
- [ ] 完整更新 app.py 使用新模組
- [ ] 測試 OAuth 整合
- [ ] 測試 WooCommerce 整合
- [ ] 測試成本計算功能

### 中優先級
- [ ] 建立 src/ui/sidebar.py (側邊欄組件)
- [ ] 建立 src/ui/charts.py (圖表組件)
- [ ] 建立 src/ui/metrics.py (指標卡片)
- [ ] 建立 src/utils/data_processor.py (數據處理)

### 低優先級
- [ ] 建立單元測試 (tests/)
- [ ] 建立多頁面應用 (pages/)
- [ ] 更新 CLAUDE.md 反映新結構
- [ ] 更新 README.md 反映新結構

---

## 🐛 已知問題

1. **Import 路徑**：如果遇到 import 錯誤，可能需要：
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **舊的 OAuth 檔案路徑**：scripts 中的檔案可能需要更新 import 路徑

3. **Streamlit Secrets**：確保 `.streamlit/secrets.toml` 包含 `oauth_redirect_uri`

---

## 📚 相關文件

- [OAUTH_SETUP.md](docs/OAUTH_SETUP.md) - OAuth 設定指南
- [META_TOKEN_SETUP.md](docs/META_TOKEN_SETUP.md) - Token 管理指南
- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - 完整結構規劃

---

**更新日期**：2025-09-30
**狀態**：🚧 重構進行中