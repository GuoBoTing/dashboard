"""
RFM 客戶分群分析模組
"""
import pandas as pd
import streamlit as st
import plotly.express as px

def analyze_rfm_customers(orders_df, reference_date):
    """
    RFM 客戶分群分析
    
    參數:
        orders_df: 訂單 DataFrame（包含 email, date, total）
        reference_date: 參考日期（通常是今天或分析截止日）
    
    返回:
        rfm_df: 包含客戶 RFM 指標和分群的 DataFrame
        segment_stats: 各客戶群統計資料
        thresholds: 消費門檻
    """
    if orders_df.empty:
        return pd.DataFrame(), {}, {}
    
    # 過濾有效 email
    valid_orders = orders_df[orders_df['email'].notna() & (orders_df['email'] != '')].copy()
    
    if valid_orders.empty:
        return pd.DataFrame(), {}, {}
    
    # 確保 date 是 datetime 類型
    valid_orders['date'] = pd.to_datetime(valid_orders['date'])
    reference_date = pd.to_datetime(reference_date)
    
    # 計算每個客戶的 RFM
    rfm = valid_orders.groupby('email').agg({
        'date': lambda x: (reference_date - x.max()).days,  # R: 最近購買天數
        'email': 'count',                                    # F: 購買次數
        'total': 'sum'                                       # M: 總消費金額
    }).rename(columns={
        'date': 'Recency',
        'email': 'Frequency', 
        'total': 'Monetary'
    })
    
    # 計算消費門檻（基於分位數）
    thresholds = {
        'high_monetary': rfm['Monetary'].quantile(0.75),  # 前 25%
        'mid_monetary': rfm['Monetary'].quantile(0.50),   # 中位數
        'low_monetary': rfm['Monetary'].quantile(0.25)    # 後 75%
    }
    
    # 客戶分群函數
    def segment_customer(row):
        R = row['Recency']
        F = row['Frequency']
        M = row['Monetary']
        
        if R <= 30 and F >= 3 and M >= thresholds['high_monetary']:
            return '重要價值客戶'
        elif R <= 60 and F >= 2 and M >= thresholds['mid_monetary']:
            return '忠誠客戶'
        elif R <= 30 and 2 <= F <= 3 and M >= thresholds['mid_monetary']:
            return '潛力客戶'
        elif R <= 30 and F == 1:
            return '新客戶'
        elif 61 <= R <= 120 and F >= 2 and M >= thresholds['mid_monetary']:
            return '流失預警'
        elif 31 <= R <= 90 and 2 <= F <= 3 and M >= thresholds['low_monetary']:
            return '需要關注'
        elif R > 120 and F >= 2:
            return '沉睡客戶'
        elif R > 180:
            return '流失客戶'
        else:
            return '其他客戶'
    
    # 應用分群
    rfm['客戶群'] = rfm.apply(segment_customer, axis=1)
    
    # 計算各群統計
    segment_stats = rfm.groupby('客戶群').agg({
        'Recency': ['count', 'mean'],
        'Frequency': 'mean',
        'Monetary': ['mean', 'sum']
    }).round(0)
    
    segment_stats.columns = ['客戶數', '平均間隔天數', '平均購買次數', '平均消費', '總貢獻']
    segment_stats['佔比'] = (segment_stats['客戶數'] / len(rfm) * 100).round(1)
    segment_stats = segment_stats[['客戶數', '佔比', '平均購買次數', '平均消費', '總貢獻', '平均間隔天數']]
    
    return rfm, segment_stats, thresholds


def show_rfm_analysis_tab(orders_df, end_date):
    """顯示 RFM 分析分頁內容"""
    st.markdown("""
    <div class="clean-section-header">
        <h2>🎯 RFM 客戶分群分析</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📊 此分析基於最近 12 個月的訂單數據進行客戶分群（首次載入約需 10-15 秒）")
    
    if not orders_df.empty:
        with st.spinner("正在分析客戶 RFM 數據..."):
            rfm_df, segment_stats, thresholds = analyze_rfm_customers(orders_df, end_date)
            
            if not rfm_df.empty:
                # 總覽指標
                col1, col2, col3, col4 = st.columns(4)
                total_customers = len(rfm_df)
                high_value = len(rfm_df[rfm_df['客戶群'] == '重要價值客戶'])
                new_customers = len(rfm_df[rfm_df['客戶群'] == '新客戶'])
                at_risk = len(rfm_df[rfm_df['客戶群'].isin(['流失預警', '沉睡客戶', '流失客戶'])])
                
                with col1:
                    st.metric("總客戶數", f"{total_customers:,}")
                with col2:
                    st.metric("重要價值客戶", f"{high_value}", f"{high_value/total_customers*100:.1f}%")
                with col3:
                    st.metric("新客戶", f"{new_customers}", f"{new_customers/total_customers*100:.1f}%")
                with col4:
                    st.metric("流失風險客戶", f"{at_risk}", f"{at_risk/total_customers*100:.1f}%")
                
                # 分群邏輯說明
                with st.expander("📖 查看分群邏輯說明", expanded=False):
                    st.markdown(f"""
                    ### 消費門檻設定（基於客戶分位數）
                    - **高消費門檻**: ${thresholds.get('high_monetary', 0):,.0f}（前 25% 客戶）
                    - **中消費門檻**: ${thresholds.get('mid_monetary', 0):,.0f}（中位數）
                    - **低消費門檻**: ${thresholds.get('low_monetary', 0):,.0f}（後 75% 客戶）
                    
                    ### 客戶分群定義
                    - 🏆 **重要價值客戶**: R ≤ 30天 & F ≥ 3次 & M ≥ 高消費門檻
                    - 💎 **忠誠客戶**: R ≤ 60天 & F ≥ 2次 & M ≥ 中消費門檻
                    - 🌱 **潛力客戶**: R ≤ 30天 & F = 2-3次 & M ≥ 中消費門檻
                    - 🆕 **新客戶**: R ≤ 30天 & F = 1次
                    - ⚠️ **流失預警**: R = 61-120天 & F ≥ 2次 & M ≥ 中消費門檻
                    - 👀 **需要關注**: R = 31-90天 & F = 2-3次 & M ≥ 低消費門檻
                    - 😴 **沉睡客戶**: R > 120天 & F ≥ 2次
                    - 💔 **流失客戶**: R > 180天
                    """)
                
                # 客戶分群分布圖
                st.markdown("""<div class="clean-section-header"><h3>客戶分群分布</h3></div>""", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    segment_counts = rfm_df['客戶群'].value_counts()
                    fig_pie = px.pie(
                        values=segment_counts.values,
                        names=segment_counts.index,
                        title='客戶群佔比',
                        hole=0.4
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    fig_bar = px.bar(
                        x=segment_counts.index,
                        y=segment_counts.values,
                        title='各客戶群人數',
                        labels={'x': '客戶群', 'y': '客戶數'},
                        color=segment_counts.values,
                        color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # 客戶分群統計表
                st.markdown("""<div class="clean-section-header"><h3>客戶分群詳細統計</h3></div>""", unsafe_allow_html=True)
                
                display_stats = segment_stats.copy()
                display_stats['平均消費'] = display_stats['平均消費'].apply(lambda x: f"${x:,.0f}")
                display_stats['總貢獻'] = display_stats['總貢獻'].apply(lambda x: f"${x:,.0f}")
                display_stats['佔比'] = display_stats['佔比'].apply(lambda x: f"{x}%")
                
                st.dataframe(display_stats, use_container_width=True)
                
                # 下載數據
                st.markdown("""<div class="clean-section-header"><h3>匯出數據</h3></div>""", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    rfm_csv = rfm_df.to_csv(index=True).encode('utf-8-sig')
                    st.download_button(
                        label="📥 下載完整 RFM 客戶數據 (CSV)",
                        data=rfm_csv,
                        file_name=f"rfm_customers_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    stats_csv = segment_stats.to_csv(index=True).encode('utf-8-sig')
                    st.download_button(
                        label="📥 下載客戶分群統計 (CSV)",
                        data=stats_csv,
                        file_name=f"rfm_segments_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("無法進行 RFM 分析，請確保訂單數據包含有效的 email 地址")
    else:
        st.warning("請先獲取訂單數據")
