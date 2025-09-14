import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# 這個版本完全不使用 plotly.graph_objects

print("開始執行 Dashboard...")  # 除錯用

# 頁面配置
st.set_page_config(
    page_title="Simple Dashboard",
    page_icon="📊",
    layout="wide"
)

# 標題
st.title("📊 簡化版 E-commerce Dashboard")
st.write("這個版本完全不使用 plotly.graph_objects")

# 建立簡單的範例數據
@st.cache_data
def create_simple_data():
    print("正在建立數據...")  # 除錯用
    dates = pd.date_range(start='2024-11-01', end='2024-11-30', freq='D')
    np.random.seed(42)
    
    data = {
        '日期': dates,
        '廣告花費': np.random.uniform(100, 500, len(dates)),
        '訂單金額': np.random.uniform(200, 1000, len(dates))
    }
    
    df = pd.DataFrame(data)
    df['ROAS'] = df['訂單金額'] / df['廣告花費']
    df['毛利'] = df['訂單金額'] * 0.4
    df['淨利潤'] = df['毛利'] - df['廣告花費']
    
    print(f"數據建立完成，共 {len(df)} 筆記錄")  # 除錯用
    return df

# 載入數據
try:
    df = create_simple_data()
    st.success("✅ 數據載入成功")
except Exception as e:
    st.error(f"❌ 錯誤: {e}")
    st.stop()

# 顯示基本資訊
st.subheader("📈 關鍵指標")

# 計算總計
total_spend = df['廣告花費'].sum()
total_revenue = df['訂單金額'].sum()
avg_roas = df['ROAS'].mean()
total_profit = df['淨利潤'].sum()

# 顯示指標 - 使用簡單的欄位佈局
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("總廣告花費", f"${total_spend:,.0f}")

with col2:
    st.metric("總訂單金額", f"${total_revenue:,.0f}")

with col3:
    st.metric("平均 ROAS", f"{avg_roas:.2f}")

with col4:
    st.metric("總淨利潤", f"${total_profit:,.0f}")

# 圖表區域
st.subheader("📊 圖表分析")

# 圖表1：簡單的線圖
try:
    fig1 = px.line(
        df, 
        x='日期', 
        y=['廣告花費', '訂單金額'],
        title='每日廣告花費 vs 訂單金額'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    print("圖表1顯示成功")  # 除錯用
    
except Exception as e:
    st.error(f"圖表1錯誤: {e}")

# 圖表2：ROAS趨勢
try:
    fig2 = px.line(
        df,
        x='日期',
        y='ROAS',
        title='ROAS 趨勢'
    )
    # 添加基準線 - 使用 plotly express 的方式
    fig2.add_hline(y=1, line_dash="dash", line_color="red")
    st.plotly_chart(fig2, use_container_width=True)
    
    print("圖表2顯示成功")  # 除錯用
    
except Exception as e:
    st.error(f"圖表2錯誤: {e}")

# 圖表3：使用 plotly express 的柱狀圖來替代複雜的面積圖
try:
    # 準備數據
    chart_data = df[['日期', '廣告花費', '訂單金額', '毛利']].copy()
    
    # 使用柱狀圖
    fig3 = px.bar(
        chart_data,
        x='日期',
        y=['廣告花費', '毛利'],
        title='每日廣告花費 vs 毛利對比',
        barmode='group'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    print("圖表3顯示成功")  # 除錯用
    
except Exception as e:
    st.error(f"圖表3錯誤: {e}")

# 圖表4：淨利潤趨勢 - 簡單線圖
try:
    fig4 = px.line(
        df,
        x='日期',
        y='淨利潤',
        title='每日淨利潤趨勢'
    )
    fig4.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig4, use_container_width=True)
    
    print("圖表4顯示成功")  # 除錯用
    
except Exception as e:
    st.error(f"圖表4錯誤: {e}")

# 數據表格
st.subheader("📋 詳細數據")
if st.checkbox("顯示數據表格"):
    # 格式化數據顯示
    display_df = df.copy()
    display_df = display_df.round(2)
    st.dataframe(display_df, use_container_width=True)

# 數據統計
st.subheader("📊 統計摘要")
col1, col2 = st.columns(2)

with col1:
    st.write("**廣告花費統計:**")
    st.write(f"- 平均: ${df['廣告花費'].mean():.2f}")
    st.write(f"- 最高: ${df['廣告花費'].max():.2f}")
    st.write(f"- 最低: ${df['廣告花費'].min():.2f}")

with col2:
    st.write("**ROAS 統計:**")
    st.write(f"- 平均: {df['ROAS'].mean():.2f}")
    st.write(f"- 最高: {df['ROAS'].max():.2f}")
    st.write(f"- 最低: {df['ROAS'].min():.2f}")

# 匯出功能
st.subheader("💾 數據匯出")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="下載 CSV 檔案",
    data=csv,
    file_name=f'simple_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
    mime='text/csv'
)

# 除錯資訊
with st.expander("🔧 除錯資訊"):
    st.write("**使用的套件版本:**")
    st.write(f"- Streamlit: {st.__version__}")
    st.write(f"- Pandas: {pd.__version__}")
    st.write(f"- Numpy: {np.__version__}")
    
    st.write("**數據基本資訊:**")
    st.write(f"- 數據筆數: {len(df)}")
    st.write(f"- 日期範圍: {df['日期'].min()} 到 {df['日期'].max()}")
    st.write(f"- 欄位: {list(df.columns)}")

# 說明
st.markdown("---")
st.markdown("""
**📖 說明:**
- 這是一個簡化版的 Dashboard
- 完全不使用 `plotly.graph_objects`
- 只使用 `plotly.express` 進行圖表繪製
- 如果這個版本能正常運行，我們再逐步增加功能
""")

print("Dashboard 執行完畢")  # 除錯用