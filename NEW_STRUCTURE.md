# 📊 新專案結構總覽

## ✅ 重構完成！

```
flambe-dashboard/
│
├── 📄 主程式
│   ├── app.py                      # 主程式入口 ⭐ (需更新 imports)
│   ├── app_backup.py               # 原始備份
│   └── REFACTOR_GUIDE.md           # 重構指南 📖
│
├── ⚙️ 配置檔案
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   └── .gitignore
│
├── 📚 文件
│   ├── README.md                   # 專案說明
│   └── CLAUDE.md                   # 開發指南
│
├── 🎨 src/ - 核心程式碼
│   ├── __init__.py
│   ├── config.py                   # ✅ 配置管理
│   ├── constants.py                # ✅ 常數定義
│   │
│   ├── api/ - API 客戶端模組
│   │   ├── __init__.py
│   │   ├── woocommerce.py          # ✅ WooCommerce API
│   │   ├── meta_ads.py             # ✅ Meta Ads API
│   │   └── meta_oauth.py           # ✅ OAuth 2.0 認證
│   │
│   ├── utils/ - 工具函數
│   │   ├── __init__.py
│   │   └── cost_calculator.py      # ✅ 成本計算
│   │
│   └── ui/ - UI 組件
│       ├── __init__.py
│       └── styles.py               # ✅ CSS 樣式
│
├── 🛠️ scripts/ - 獨立腳本
│   ├── meta_debug.py               # ✅ Meta API 調試工具
│   ├── meta_api_test.py            # ✅ API 測試
│   └── oauth_example.py            # ✅ OAuth 範例應用
│
├── 📖 docs/ - 文件目錄
│   ├── META_API_修復指南.md        # Meta API 故障排除
│   ├── META_TOKEN_SETUP.md         # Token 管理說明
│   ├── OAUTH_SETUP.md              # OAuth 設定指南
│   ├── CURRENT_STRUCTURE.md        # 舊結構分析
│   └── PROJECT_STRUCTURE.md        # 結構規劃
│
├── 🧪 tests/ - 測試目錄
│   └── __init__.py
│
└── 💾 data/ - 數據目錄
    ├── .gitkeep
    └── exports/                    # CSV 匯出檔案
```

## 📊 統計資訊

### 檔案數量
- Python 檔案：15
- 文件檔案：8
- 總計：23+

### 程式碼分布
- **src/**: 8 個模組
  - api/: 3 個 API 客戶端
  - utils/: 1 個工具模組
  - ui/: 1 個 UI 模組
- **scripts/**: 3 個獨立腳本
- **docs/**: 5 個文件

## 🎯 核心模組功能

### src/api/
| 模組 | 功能 | 狀態 |
|------|------|------|
| woocommerce.py | WooCommerce 訂單數據獲取 | ✅ 完成 |
| meta_ads.py | Meta 廣告數據 + Token 刷新 | ✅ 完成 |
| meta_oauth.py | OAuth 2.0 完整流程 | ✅ 完成 |

### src/utils/
| 模組 | 功能 | 狀態 |
|------|------|------|
| cost_calculator.py | 運費、手續費、稅務計算 | ✅ 完成 |

### src/ui/
| 模組 | 功能 | 狀態 |
|------|------|------|
| styles.py | CSS 樣式 + UI 組件 | ✅ 完成 |

## 🔄 下一步

### 1. 立即測試（推薦）

```bash
# 測試新模組
python3 -c "from src.constants import SHIPPING_COSTS; print('✅')"

# 測試 OAuth 範例
streamlit run scripts/oauth_example.py
```

### 2. 更新主程式

參考 `REFACTOR_GUIDE.md` 更新 `app.py` 的 imports

### 3. 測試整合

```bash
streamlit run app.py
```

## 📋 與舊結構對比

| 舊結構 | 新結構 | 改進 |
|--------|--------|------|
| config.py | src/config.py | ✅ 模組化 |
| meta_api_enhanced.py | src/api/meta_ads.py | ✅ 重新命名 |
| meta_oauth.py | src/api/meta_oauth.py | ✅ 移到 api/ |
| (分散在 app.py) | src/constants.py | ✅ 獨立常數 |
| (分散在 app.py) | src/utils/cost_calculator.py | ✅ 功能獨立 |
| (分散在 app.py) | src/ui/styles.py | ✅ UI 分離 |
| meta_debug.py | scripts/meta_debug.py | ✅ 工具腳本分類 |
| META_API_修復指南.md | docs/META_API_修復指南.md | ✅ 文件集中 |

## 🎉 重構優勢

1. **✅ 模組化**：功能清晰分離，易於維護
2. **✅ 可重用**：API 和工具函數可獨立使用
3. **✅ 可測試**：每個模組都可獨立測試
4. **✅ 清晰**：專案結構一目了然
5. **✅ 擴展性**：新增功能時有明確的位置
6. **✅ 文件化**：完整的設定和使用指南

---

**建立日期**：2025-09-30
**專案版本**：v2.0 (重構版)
**狀態**：🎯 結構重組完成，待整合測試
