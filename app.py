# app.py - 簡化版（除錯用）
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import numpy as np

# 先暫時註解掉可能有問題的導入
try:
    from config import Config, setup_api_connections, get_active_config
    # from meta_api_enhanced import get_enhanced_meta_ads_data, show_token_management, MetaAdsAPI
    SECURE_MODE = True
    st.success("✅ 基本配置模組載入成功")
except ImportError as e:
    SECURE_MODE = False
    st.error(f"❌ 配置模組載入失敗: {str(e)}")

# 頁面設定
st.set_page_config(
    page_title="商業分析儀表板",
    page_icon="📊",
    layout="wide"
)

# 基本測試
st.title("🔧 系統狀態檢查")

if SECURE_MODE:
    st.success("🔒 安全模式：配置模組正常")
    
    # 測試配置功能
    try:
        config = Config()
        wc_configured, meta_configured = config.is_configured()
        st.write(f"WooCommerce 配置: {'✅' if wc_configured else '❌'}")
        st.write(f"Meta 配置: {'✅' if meta_configured else '❌'}")
        
        if wc_configured:
            wc_config = config.get_woocommerce_config()
            st.write("WooCommerce URL:", wc_config.get('url', 'N/A'))
        
        if meta_configured:
            meta_config = config.get_meta_config()
            st.write("Meta App ID:", meta_config.get('app_id', 'N/A'))
            
    except Exception as e:
        st.error(f"配置測試失敗: {str(e)}")
else:
    st.warning("⚠️ 基本模式：手動輸入模式")

# 簡化的 Token 管理界面
if SECURE_MODE:
    with st.expander("🔑 簡化 Token 管理"):
        st.info("Token 管理功能測試")
        short_token = st.text_input("短期 Access Token", type="password")
        
        if st.button("測試 Token 轉換") and short_token:
            st.info("Token 轉換功能暫時停用（除錯中）")

# 測試基本功能
st.subheader("📊 基本功能測試")

# 測試日期選擇
date_range = st.date_input(
    "選擇日期範圍", 
    value=(datetime.now() - timedelta(days=7), datetime.now())
)

# 測試圖表
if len(date_range) == 2:
    test_data = {
        'date': pd.date_range(date_range[0], date_range[1]),
        'revenue': np.random.uniform(1000, 5000, len(pd.date_range(date_range[0], date_range[1]))),
        'cost': np.random.uniform(500, 2000, len(pd.date_range(date_range[0], date_range[1])))
    }
    test_df = pd.DataFrame(test_data)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.line(test_df, x='date', y=['revenue', 'cost'], title='測試圖表 - 營收 vs 成本')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(test_df, x='date', y='revenue', title='測試圖表 - 每日營收')
        st.plotly_chart(fig2, use_container_width=True)

# 測試 DataFrame
st.subheader("📋 DataFrame 測試")
test_payment_data = {
    '付款方式': ['信用卡', 'Line Pay', '超商取貨'],
    '訂單數': [50, 30, 20],
    '總金額': ['$50,000', '$30,000', '$20,000']
}
test_payment_df = pd.DataFrame(test_payment_data)
st.dataframe(test_payment_df, use_container_width=True, hide_index=True)

st.success("✅ 基本功能測試完成")

# 系統資訊
with st.expander("🔍 系統資訊"):
    st.write("Streamlit 版本:", st.__version__)
    st.write("Python 版本:", pd.__version__)
    st.write("Pandas 版本:", pd.__version__)
    st.write("Plotly 版本:", px.__version__ if hasattr(px, '__version__') else 'Unknown')
    
    # 檢查可用模組
    try:
        import config
        st.write("✅ config.py 可導入")
    except Exception as e:
        st.write(f"❌ config.py 導入失敗: {e}")
    
    try:
        import meta_api_enhanced
        st.write("✅ meta_api_enhanced.py 可導入")
    except Exception as e:
        st.write(f"❌ meta_api_enhanced.py 導入失敗: {e}")

st.markdown("---")
st.info("🛠️ 這是除錯版本，用於檢查系統狀態。如果此版本正常運行，我們可以逐步恢復完整功能。")