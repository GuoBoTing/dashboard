# 性能優化總結

## 問題診斷

當點擊「顯示詳細數據」時，應用程式需要很長時間載入的**根本原因**：

### 主要瓶頸

1. **缺少快取機制（最嚴重）**
   - 每次勾選 checkbox 或切換 tab 時，Streamlit 重新執行整個腳本
   - WooCommerce 和 Meta API 被重複調用
   - 歷史訂單查詢（12個月數據）每次都重新執行

2. **歷史訂單查詢耗時**
   - `calculate_new_customer_rate` 調用 `get_historical_emails`
   - 每次查詢最近12個月的所有訂單（最多5000筆，50頁 API 請求）
   - 即使日期範圍相同，也會重新查詢

3. **低效的數據格式化**
   - 使用 `.apply(lambda x: ...)` 對每一行數據進行格式化
   - 大量訂單時會造成性能問題

## 已實施的優化

### 1. API 快取優化 ⭐ **最重要**

#### `get_historical_emails` 函數（第229行）
```python
@st.cache_data(ttl=3600, show_spinner=False)  # 快取1小時
```
- **影響**：歷史訂單數據不常變化，1小時快取大幅減少 API 調用
- **效果**：從每次查詢50頁降至1小時內只查詢一次

#### `get_enhanced_woocommerce_data` 函數（第347行）
```python
@st.cache_data(ttl=300, show_spinner=False)  # 快取5分鐘
```
- **影響**：相同日期範圍的訂單數據在5分鐘內重複使用
- **效果**：避免重複的 WooCommerce API 調用

#### `get_meta_ads_data_basic` 函數（第404行）
```python
@st.cache_data(ttl=300, show_spinner=False)  # 快取5分鐘
```
- **影響**：Meta 廣告數據在5分鐘內重複使用
- **效果**：避免重複的 Meta API 調用

### 2. 數據格式化優化

#### Tab1 - 每日營收與成本（第715-728行）
**之前**：使用迴圈 + `.apply()` 格式化7個欄位
```python
for col in ['revenue', 'estimated_cogs', ...]:
    daily_cost_df[col] = daily_cost_df[col].apply(lambda x: f"${x:,.2f}")
```

**之後**：使用 Streamlit 原生 `column_config`
```python
column_config = {col: st.column_config.NumberColumn(col, format="$%.2f")
                 for col in money_columns}
st.dataframe(..., column_config=column_config)
```
- **優勢**：瀏覽器端渲染，不佔用 Python 運算資源

#### Tab2 - 每日績效（第730-743行）
**之前**：3次 `.apply()` 操作
**之後**：使用 `column_config` 直接格式化

#### Tab3 - 訂單明細（第745-760行）
**之前**：對所有訂單的金額欄位使用 `.apply()`
**之後**：`st.column_config.NumberColumn` 格式化

#### Tab4 - 廣告績效（第762-785行）
**之前**：7次條件判斷 + `.apply()` 操作
**之後**：使用 `column_config` 字典統一管理格式

## 性能改善預期

### 首次載入
- **快取前**：需要完整查詢所有 API（WooCommerce + Meta + 歷史12個月）
- **快取後**：相同（首次必須查詢）

### 後續互動（點擊 checkbox、切換 tab）
- **快取前**：每次都重新查詢所有 API（耗時10-30秒+）
- **快取後**：直接使用快取數據（耗時<1秒）

### 具體改善
- **歷史訂單查詢**：從每次20-30秒 → 1小時內只需一次
- **WooCommerce 數據**：從每次3-5秒 → 5分鐘內只需一次
- **Meta 廣告數據**：從每次2-3秒 → 5分鐘內只需一次
- **數據格式化**：從0.5-2秒 → 幾乎即時（瀏覽器渲染）

## 快取策略說明

### TTL（Time-To-Live）設定

| 函數 | TTL | 理由 |
|------|-----|------|
| `get_historical_emails` | 1小時 (3600秒) | 歷史12個月數據變化極少 |
| `get_enhanced_woocommerce_data` | 5分鐘 (300秒) | 平衡數據新鮮度與性能 |
| `get_meta_ads_data_basic` | 5分鐘 (300秒) | Meta 數據有1-2天延遲，5分鐘已足夠 |

### 快取失效時機

快取會在以下情況自動失效：
1. **TTL 過期**：超過設定時間後自動清除
2. **參數變更**：日期範圍、API 金鑰等參數改變時
3. **手動清除**：用戶按 `C` 清除快取

## 使用建議

### 開發/測試環境
- 如需立即看到數據更新，按 `C` 清除快取
- 或在側邊欄更改日期範圍觸發重新查詢

### 生產環境
- 快取設定已優化，無需調整
- 每5分鐘會自動更新訂單和廣告數據
- 歷史客戶數據每小時更新一次

## 未來優化建議

1. **使用 `st.session_state` 儲存處理後的數據**
   - 避免每次重新計算成本、新客率等指標

2. **實作增量更新**
   - 只查詢新增的訂單，而非每次全量查詢

3. **背景任務**
   - 使用定時任務預先載入和快取數據

4. **資料庫快取**
   - 將 API 數據存入本地資料庫，減少 API 依賴

## 變更檔案

- `app.py` - 主要優化檔案
  - 第229行：`get_historical_emails` 快取
  - 第347行：`get_enhanced_woocommerce_data` 快取
  - 第404行：`get_meta_ads_data_basic` 快取
  - 第715-785行：數據格式化優化

## 測試建議

1. **測試快取效果**
   ```bash
   # 啟動應用
   streamlit run app.py

   # 首次點擊「顯示詳細數據」- 會較慢（需要查詢 API）
   # 取消勾選再重新勾選 - 應該立即顯示（使用快取）
   # 切換不同 tab - 應該流暢無延遲
   ```

2. **驗證數據正確性**
   - 確認快取的數據與實際 API 返回一致
   - 更改日期範圍後，數據應正確更新

3. **監控記憶體使用**
   - 快取會佔用記憶體，但以5分鐘-1小時 TTL 應不會造成問題

---

**優化完成日期**：2025-12-13
**優化類型**：性能優化（快取 + 數據格式化）
**預期效果**：載入時間從 10-30秒+ 降至 <1秒（使用快取時）
