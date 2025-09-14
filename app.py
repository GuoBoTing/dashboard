import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import numpy as np

# Import custom modules
from config import setup_api_connections, get_active_config
from meta_api_enhanced import get_enhanced_meta_ads_data, show_token_management

# 頁面設定
st.set_page_config(
    page_title="商業分析儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 樣式 - 移除箭頭和邊框
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .clean-section-header {
        background: #f8fafc;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .clean-section-header h2 {
        margin: 0;
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* 隱藏所有箭頭 */
    [data-testid="metric-container"] svg,
    .metric-container svg,
    .st-emotion-cache-5znelh svg,
    .e1lfzwz56 svg,
    div[data-testid="metric-container"] > div > div > div > svg,
    .metric-container .element-container svg,
    [class*="metric"] svg,
    [class*="delta"] svg {
        display: none !important;
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# 設定參數
SHIPPING_COSTS = {
    "全家便利商店": 69, "萊爾富": 58, "宅配": 180, "全家": 69, "超商取貨": 60, "Unknown": 0, "未知": 0
}

PAYMENT_FEES = {
    "超商取貨付款": 0.53, "Line Pay": 2.94, "信用卡": 2.5725, "貨到付款": 0.53,
    "ATM轉帳": 0.0, "Unknown": 0.0, "未知": 0.0
}

TAX_RATE = 0.05  # 5%

# 主標題
st.markdown("""
<div class="main-header">
    <h1>電商業績分析儀表板</h1>
    <p>WooCommerce 與 Meta 廣告整合分析平台</p>
</div>
""", unsafe_allow_html=True)

# 側邊欄
with st.sidebar:
    st.header("設定面板")
    st.markdown("---")
    
    # Setup API connections using the configuration management system
    connection_status = setup_api_connections()
    
    st.markdown("---")
    st.subheader("成本設定")
    cogs_rate = st.slider("估計進貨成本率 (%)", min_value=20, max_value=80, value=50, step=5)
    
    st.subheader("分析期間")
    date_range = st.date_input("選擇日期範圍", 
                               value=(datetime.now() - timedelta(days=30), datetime.now()),
                               max_value=datetime.now())
    
    # Get active configuration
    active_config = get_active_config()
    wc_configured = active_config.get('woocommerce_configured', False)
    meta_configured = active_config.get('meta_configured', False)
    
    st.markdown("---")
    st.subheader("連接狀態")
    st.write(f"WooCommerce: {'🟢 已連接' if wc_configured else '🔴 未連接'}")
    st.write(f"Meta 廣告: {'🟢 已連接' if meta_configured else '🔴 未連接'}")
    
    # Add token management section
    if meta_configured:
        st.markdown("---")
        with st.expander("🔑 Meta Token 管理", expanded=False):
            show_token_management()

# 計算函數
def calculate_shipping_costs(shipping_methods):
    shipping_costs = {}
    total_shipping_cost = 0
    for method, count in shipping_methods.items():
        cost_per_order = 0
        for key, cost in SHIPPING_COSTS.items():
            if key.lower() in method.lower() or method.lower() in key.lower():
                cost_per_order = cost
                break
        total_cost = cost_per_order * count
        shipping_costs[method] = {'count': count, 'cost_per_order': cost_per_order, 'total_cost': total_cost}
        total_shipping_cost += total_cost
    return shipping_costs, total_shipping_cost

def calculate_payment_fees(orders_df):
    payment_fees = {}
    total_payment_fee = 0
    if not orders_df.empty:
        payment_summary = orders_df.groupby('payment_method').agg({'total': ['count', 'sum']}).round(2)
        payment_summary.columns = ['order_count', 'total_amount']
        payment_summary = payment_summary.reset_index()
        
        for _, row in payment_summary.iterrows():
            method, count, amount = row['payment_method'], int(row['order_count']), float(row['total_amount'])
            fee_rate = 0.0
            for key, rate in PAYMENT_FEES.items():
                if key.lower() in method.lower() or method.lower() in key.lower():
                    fee_rate = rate
                    break
            fee_amount = amount * (fee_rate / 100)
            payment_fees[method] = {'count': count, 'total_amount': amount, 'fee_rate': fee_rate, 'fee_amount': fee_amount}
            total_payment_fee += fee_amount
    return payment_fees, total_payment_fee

def get_enhanced_woocommerce_data(url, key, secret, start_date, end_date):
    try:
        clean_url = url.rstrip('/')
        endpoint = f"{clean_url}/wp-json/wc/v3/orders"
        auth = HTTPBasicAuth(key, secret)
        params = {
            'after': start_date.strftime('%Y-%m-%d') + 'T00:00:00',
            'before': end_date.strftime('%Y-%m-%d') + 'T23:59:59',
            'per_page': 100, 'status': 'completed,processing,on-hold', 'orderby': 'date', 'order': 'desc'
        }
        
        with st.spinner("正在獲取 WooCommerce 數據..."):
            all_orders, page = [], 1
            while True:
                params['page'] = page
                response = requests.get(endpoint, auth=auth, params=params, timeout=30)
                if response.status_code == 200:
                    orders = response.json()
                    if not orders: break
                    all_orders.extend(orders)
                    page += 1
                    if len(all_orders) >= 1000: break
                else:
                    if page == 1:
                        st.error(f"WooCommerce API 錯誤: {response.text}")
                        return pd.DataFrame(), {}, {}
                    else: break
            
            order_data, payment_methods, shipping_methods = [], {}, {}
            for order in all_orders:
                order_info = {
                    'order_id': order['id'], 'date': pd.to_datetime(order['date_created']).date(),
                    'total': float(order['total']), 'status': order['status'],
                    'customer_id': order.get('customer_id', 0),
                    'payment_method': order.get('payment_method_title', '未知'), 'shipping_method': '未知'
                }
                payment_method = order.get('payment_method_title', '未知')
                payment_methods[payment_method] = payment_methods.get(payment_method, 0) + 1
                
                shipping_lines = order.get('shipping_lines', [])
                if shipping_lines:
                    shipping_method = shipping_lines[0].get('method_title', '未知')
                    order_info['shipping_method'] = shipping_method
                    shipping_methods[shipping_method] = shipping_methods.get(shipping_method, 0) + 1
                else:
                    shipping_methods['未知'] = shipping_methods.get('未知', 0) + 1
                order_data.append(order_info)
            
            df = pd.DataFrame(order_data)
            st.success(f"成功獲取 {len(all_orders)} 筆 WooCommerce 訂單")
            return df, payment_methods, shipping_methods
    except Exception as e:
        st.error(f"WooCommerce 連接錯誤: {str(e)}")
        return pd.DataFrame(), {}, {}


# 主要分析
if len(date_range) == 2:
    start_date, end_date = date_range
    
    if wc_configured or meta_configured:
        orders_df, payment_methods, shipping_methods, ads_df = pd.DataFrame(), {}, {}, pd.DataFrame()
        
        if wc_configured:
            # Get WooCommerce configuration
            wc_config = active_config.get('woocommerce', {})
            orders_df, payment_methods, shipping_methods = get_enhanced_woocommerce_data(
                wc_config.get('url', ''), 
                wc_config.get('consumer_key', ''), 
                wc_config.get('consumer_secret', ''), 
                start_date, 
                end_date
            )
        if meta_configured:
            # Use enhanced Meta API client
            meta_config = active_config.get('meta', {})
            ads_df = get_enhanced_meta_ads_data(meta_config, date_preset='last_30d', level='campaign')
        
        if not orders_df.empty or not ads_df.empty:
            # 計算基本指標
            if not orders_df.empty:
                total_revenue, total_orders = orders_df['total'].sum(), len(orders_df)
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            else:
                total_revenue = total_orders = avg_order_value = 0
            
            if not ads_df.empty:
                total_ad_spend = ads_df['spend'].sum()
                total_impressions, total_clicks = ads_df['impressions'].sum(), ads_df['clicks'].sum()
            else:
                total_ad_spend = total_impressions = total_clicks = 0
            
            # 計算成本
            estimated_cogs = total_revenue * (cogs_rate / 100)
            shipping_costs_detail, total_shipping_cost = calculate_shipping_costs(shipping_methods)
            payment_fees_detail, total_payment_fee = calculate_payment_fees(orders_df)
            business_tax = total_revenue * TAX_RATE
            
            # 計算總成本和淨利
            total_all_costs = estimated_cogs + total_shipping_cost + total_payment_fee + total_ad_spend + business_tax
            estimated_net_profit = total_revenue - total_all_costs
            roas = total_revenue / total_ad_spend if total_ad_spend > 0 else 0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            
            # 營運總覽
            st.markdown("""<div class="clean-section-header"><h2>營運總覽</h2></div>""", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("總營收", f"${total_revenue:,.0f}")
            with col2: st.metric("總訂單數", f"{total_orders:,}")
            with col3: st.metric("客單價", f"${avg_order_value:.0f}")
            with col4: st.metric("估計淨利", f"${estimated_net_profit:,.0f}")
            
            # 成本分析
            st.markdown(f"""<div class="clean-section-header"><h2>成本分析（總成本：${total_all_costs:,.0f}）</h2></div>""", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: st.metric("估計進貨成本", f"${estimated_cogs:,.0f}")
            with col2: st.metric("運費", f"${total_shipping_cost:,.0f}")
            with col3: st.metric("金流服務費", f"${total_payment_fee:,.0f}")
            with col4: st.metric("廣告費", f"${total_ad_spend:,.0f}")
            with col5: st.metric("營業稅", f"${business_tax:,.0f}")
            
            # 廣告數據
            if not ads_df.empty:
                st.markdown("""<div class="clean-section-header"><h2>廣告數據</h2></div>""", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("總曝光", f"{total_impressions:,}")
                with col2: st.metric("總點擊", f"{total_clicks:,}")
                with col3: st.metric("點擊率", f"{ctr:.2f}%")
                with col4: st.metric("ROAS", f"{roas:.2f}")
            
            # 成本結構分析
            st.header("成本結構分析")
            col1, col2 = st.columns(2)
            
            with col1:
                cost_structure = {'估計進貨成本': estimated_cogs, '廣告費': total_ad_spend, '運費': total_shipping_cost, '金流服務費': total_payment_fee, '營業稅': business_tax}
                filtered_costs = {k: v for k, v in cost_structure.items() if v > 0}
                
                if filtered_costs:
                    cost_df = pd.DataFrame(list(filtered_costs.items()), columns=['成本類型', '金額'])
                    fig_cost = px.pie(cost_df, values='金額', names='成本類型', title='成本結構分布')
                    fig_cost.update_traces(textposition='inside', textinfo='percent+label')
                    fig_cost.update_layout(height=400)
                    st.plotly_chart(fig_cost, use_container_width=True)
            
            with col2:
                financial_summary = {'總營收': total_revenue, '總成本': total_all_costs, '估計淨利': estimated_net_profit}
                summary_df = pd.DataFrame(list(financial_summary.items()), columns=['項目', '金額'])
                fig_summary = px.bar(summary_df, x='項目', y='金額', title='營收、成本與獲利比較',
                                   color='金額', color_continuous_scale=['red', 'yellow', 'green'])
                fig_summary.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_summary, use_container_width=True)
            
            # 付款方式分析
            if payment_methods:
                st.header("付款方式分析")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    payment_data = []
                    for method, details in payment_fees_detail.items():
                        payment_data.append({
                            '付款方式': method, '訂單數': details['count'],
                            '總金額': f"${details['total_amount']:,.0f}", '手續費率': f"{details['fee_rate']}%",
                            '手續費': f"${details['fee_amount']:,.0f}", '占比': f"{(details['count']/total_orders*100):.1f}%"
                        })
                    payment_df = pd.DataFrame(payment_data).sort_values('訂單數', ascending=False)
                    st.subheader("付款方式統計")
                    st.dataframe(payment_df, use_container_width=True, hide_index=True)
                
                with col2:
                    payment_chart_df = pd.DataFrame(list(payment_methods.items()), columns=['付款方式', '訂單數'])
                    fig_payment = px.pie(payment_chart_df, values='訂單數', names='付款方式', title='付款方式分布')
                    fig_payment.update_traces(textposition='inside', textinfo='percent+label')
                    fig_payment.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_payment, use_container_width=True)
            
            # 運送方式分析
            if shipping_methods:
                st.header("運送方式分析")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    shipping_data = []
                    for method, details in shipping_costs_detail.items():
                        shipping_data.append({
                            '運送方式': method, '訂單數': details['count'], '單筆運費': f"${details['cost_per_order']}",
                            '總運費': f"${details['total_cost']:,.0f}", '占比': f"{(details['count']/total_orders*100):.1f}%"
                        })
                    shipping_df = pd.DataFrame(shipping_data).sort_values('訂單數', ascending=False)
                    st.subheader("運送方式統計")
                    st.dataframe(shipping_df, use_container_width=True, hide_index=True)
                
                with col2:
                    shipping_chart_df = pd.DataFrame(list(shipping_methods.items()), columns=['運送方式', '訂單數'])
                    fig_shipping = px.bar(shipping_chart_df, x='運送方式', y='訂單數', title='運送方式偏好',
                                        color='訂單數', color_continuous_scale='Blues')
                    fig_shipping.update_layout(xaxis_tickangle=-45, height=400, showlegend=False)
                    st.plotly_chart(fig_shipping, use_container_width=True)
            
            # 趨勢分析
            st.header("趨勢分析")
            
            # 合併每日數據
            if not orders_df.empty and not ads_df.empty:
                daily_orders = orders_df.groupby('date')['total'].sum().reset_index()
                daily_ads = ads_df.groupby('date')['spend'].sum().reset_index()
                merged_df = pd.merge(daily_orders, daily_ads, on='date', how='outer').fillna(0)
                merged_df.rename(columns={'total': 'revenue'}, inplace=True)
            elif not orders_df.empty:
                merged_df = orders_df.groupby('date')['total'].sum().reset_index()
                merged_df.rename(columns={'total': 'revenue'}, inplace=True)
                merged_df['spend'] = 0
            else:
                merged_df = ads_df.groupby('date')['spend'].sum().reset_index()
                merged_df['revenue'] = 0
            
            # 計算每日指標
            merged_df['roas'] = merged_df['revenue'] / merged_df['spend'].replace(0, 1)
            days_count = len(merged_df)
            merged_df['estimated_cogs'] = merged_df['revenue'] * (cogs_rate / 100)
            merged_df['daily_shipping_cost'] = total_shipping_cost / days_count if days_count > 0 else 0
            merged_df['daily_payment_fee'] = total_payment_fee / days_count if days_count > 0 else 0
            merged_df['business_tax'] = merged_df['revenue'] * TAX_RATE
            merged_df['estimated_net_profit'] = (merged_df['revenue'] - merged_df['estimated_cogs'] - 
                                               merged_df['daily_shipping_cost'] - merged_df['daily_payment_fee'] - 
                                               merged_df['spend'] - merged_df['business_tax'])
            
            # 圖表
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.line(merged_df, x='date', y=['revenue', 'spend'], title='每日營收 vs 廣告支出',
                              labels={'value': '金額 ($)', 'variable': '指標'})
                fig1.update_layout(height=400)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                if not merged_df.empty and 'roas' in merged_df.columns:
                    fig2 = px.line(merged_df, x='date', y='roas', title='ROAS 趨勢')
                    fig2.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="損益平衡")
                    fig2.add_hline(y=3, line_dash="dot", line_color="green", annotation_text="目標值")
                    fig2.update_layout(height=400)
                    st.plotly_chart(fig2, use_container_width=True)
            
            # 每日淨利圖表
            st.subheader("每日估計淨利分析")
            fig3 = px.bar(merged_df, x='date', y='estimated_net_profit', title='每日估計淨利',
                         color='estimated_net_profit', color_continuous_scale=['red', 'yellow', 'green'],
                         labels={'estimated_net_profit': '估計淨利 ($)', 'date': '日期'})
            fig3.add_hline(y=0, line_dash="solid", line_color="black", annotation_text="損益平衡線")
            fig3.update_layout(height=450)
            st.plotly_chart(fig3, use_container_width=True)
            
            # 淨利統計摘要
            if not merged_df.empty:
                st.markdown("### 淨利統計摘要")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    avg_daily_profit = merged_df['estimated_net_profit'].mean()
                    st.metric("平均每日淨利", f"${avg_daily_profit:,.0f}")
                with col2:
                    max_daily_profit = merged_df['estimated_net_profit'].max()
                    best_day = merged_df[merged_df['estimated_net_profit'] == max_daily_profit]['date'].iloc[0]
                    st.metric("最高單日淨利", f"${max_daily_profit:,.0f}")
                    st.caption(f"日期: {best_day}")
                with col3:
                    min_daily_profit = merged_df['estimated_net_profit'].min()
                    worst_day = merged_df[merged_df['estimated_net_profit'] == min_daily_profit]['date'].iloc[0]
                    st.metric("最低單日淨利", f"${min_daily_profit:,.0f}")
                    st.caption(f"日期: {worst_day}")
                with col4:
                    profitable_days = len(merged_df[merged_df['estimated_net_profit'] > 0])
                    total_days = len(merged_df)
                    profit_rate = (profitable_days / total_days * 100) if total_days > 0 else 0
                    st.metric("獲利天數比例", f"{profit_rate:.1f}%")
                    st.caption(f"{profitable_days}/{total_days} 天")
            
            # 詳細數據表格
            if st.checkbox("顯示詳細數據"):
                st.header("詳細分析數據")
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["每日營收與成本", "每日績效", "訂單明細", "廣告績效", "成本明細"])
                
                with tab1:
                    if 'merged_df' in locals() and not merged_df.empty:
                        daily_cost_df = merged_df[['date', 'revenue', 'estimated_cogs', 'daily_shipping_cost', 
                                                 'daily_payment_fee', 'spend', 'business_tax', 'estimated_net_profit']].copy()
                        for col in ['revenue', 'estimated_cogs', 'daily_shipping_cost', 'daily_payment_fee', 'spend', 'business_tax', 'estimated_net_profit']:
                            daily_cost_df[col] = daily_cost_df[col].apply(lambda x: f"${x:,.2f}")
                        daily_cost_df = daily_cost_df.rename(columns={
                            'date': '日期', 'revenue': '營收', 'estimated_cogs': '估計進貨成本',
                            'daily_shipping_cost': '運費', 'daily_payment_fee': '金流服務費',
                            'spend': '廣告費', 'business_tax': '營業稅', 'estimated_net_profit': '估計淨利'
                        })
                        st.dataframe(daily_cost_df, use_container_width=True, hide_index=True)
                        st.info("💡 提示：運費和金流服務費按日平均分配計算")
                
                with tab2:
                    if 'merged_df' in locals() and not merged_df.empty:
                        display_df = merged_df[['date', 'revenue', 'spend', 'roas']].copy()
                        for col in ['revenue', 'spend']:
                            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
                        display_df['roas'] = display_df['roas'].apply(lambda x: f"{x:.2f}")
                        display_df = display_df.rename(columns={'date': '日期', 'revenue': '營收', 'spend': '廣告支出', 'roas': 'ROAS'})
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                with tab3:
                    if not orders_df.empty:
                        display_orders = orders_df.copy()
                        display_orders['total'] = display_orders['total'].apply(lambda x: f"${x:.2f}")
                        display_orders = display_orders.rename(columns={
                            'order_id': '訂單ID', 'date': '日期', 'total': '金額', 'status': '狀態',
                            'customer_id': '客戶ID', 'payment_method': '付款方式', 'shipping_method': '運送方式'
                        })
                        st.dataframe(display_orders, use_container_width=True, hide_index=True)
                
                with tab4:
                    if not ads_df.empty:
                        display_ads = ads_df.copy()
                        for col in ['spend', 'cpm', 'cpc']:
                            if col in display_ads.columns:
                                display_ads[col] = display_ads[col].apply(lambda x: f"${x:.2f}")
                        for col in ['impressions', 'clicks', 'reach']:
                            if col in display_ads.columns:
                                display_ads[col] = display_ads[col].apply(lambda x: f"{x:,}")
                        if 'ctr' in display_ads.columns:
                            display_ads['ctr'] = display_ads['ctr'].apply(lambda x: f"{x:.2f}%")
                        display_ads = display_ads.rename(columns={
                            'date': '日期', 'spend': '廣告支出', 'impressions': '曝光數', 'clicks': '點擊數',
                            'reach': '觸及人數', 'ctr': '點擊率', 'cpm': '千次曝光成本', 'cpc': '單次點擊成本'
                        })
                        st.dataframe(display_ads, use_container_width=True, hide_index=True)
                
                with tab5:
                    cost_details = []
                    cost_details.append({
                        '成本類型': '估計進貨成本', '項目': f'{cogs_rate}% 成本率',
                        '基準金額': f"${total_revenue:,.0f}", '費率/單價': f"{cogs_rate}%", '總額': f"${estimated_cogs:,.0f}"
                    })
                    
                    if shipping_costs_detail:
                        for method, details in shipping_costs_detail.items():
                            if details['total_cost'] > 0:
                                cost_details.append({
                                    '成本類型': '運費', '項目': method, '基準金額': f"{details['count']} 筆訂單",
                                    '費率/單價': f"${details['cost_per_order']}", '總額': f"${details['total_cost']:,.0f}"
                                })
                    
                    if payment_fees_detail:
                        for method, details in payment_fees_detail.items():
                            if details['fee_amount'] > 0:
                                cost_details.append({
                                    '成本類型': '金流服務費', '項目': method, '基準金額': f"${details['total_amount']:,.0f}",
                                    '費率/單價': f"{details['fee_rate']}%", '總額': f"${details['fee_amount']:,.0f}"
                                })
                    
                    if total_ad_spend > 0:
                        cost_details.append({
                            '成本類型': '廣告費', '項目': 'Meta 廣告', '基準金額': '-',
                            '費率/單價': '-', '總額': f"${total_ad_spend:,.0f}"
                        })
                    
                    cost_details.append({
                        '成本類型': '營業稅', '項目': '5% 營業稅', '基準金額': f"${total_revenue:,.0f}",
                        '費率/單價': '5%', '總額': f"${business_tax:,.0f}"
                    })
                    
                    if cost_details:
                        cost_df = pd.DataFrame(cost_details)
                        st.dataframe(cost_df, use_container_width=True, hide_index=True)
                        
                        st.subheader("成本摘要")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write("**商品相關成本**")
                            st.write(f"估計進貨成本: ${estimated_cogs:,.0f}")
                            st.write(f"運費: ${total_shipping_cost:,.0f}")
                            st.write(f"金流服務費: ${total_payment_fee:,.0f}")
                        with col2:
                            st.write("**行銷成本**")
                            st.write(f"廣告費: ${total_ad_spend:,.0f}")
                        with col3:
                            st.write("**稅務與總計**")
                            st.write(f"營業稅: ${business_tax:,.0f}")
                            st.write(f"**總成本: ${total_all_costs:,.0f}**")
                            st.write(f"**估計淨利: ${estimated_net_profit:,.0f}**")
            
            # 數據匯出
            st.header("數據匯出")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'merged_df' in locals():
                    csv_data = merged_df.to_csv(index=False)
                    st.download_button("下載每日數據", data=csv_data, 
                                     file_name=f"每日數據_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
            
            with col2:
                if payment_methods and 'payment_df' in locals():
                    payment_csv = payment_df.to_csv(index=False)
                    st.download_button("下載付款分析", data=payment_csv,
                                     file_name=f"付款分析_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
            
            with col3:
                if shipping_methods and 'shipping_df' in locals():
                    shipping_csv = shipping_df.to_csv(index=False)
                    st.download_button("下載運送分析", data=shipping_csv,
                                     file_name=f"運送分析_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
            
            with col4:
                if 'daily_cost_df' in locals():
                    cost_csv = daily_cost_df.to_csv(index=False)
                    st.download_button("下載成本分析", data=cost_csv,
                                     file_name=f"成本分析_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
        else:
            st.warning("無法獲取數據，請檢查 API 連接設定")
    else:
        st.info("請在左側面板設定 API 連接以查看真實數據")
else:
    st.info("請選擇完整的分析日期範圍")

# 使用說明
with st.expander("使用說明"):
    st.markdown("""
    ### 電商業績分析儀表板
    
    **營運總覽**
    - 總營收：所有完成訂單的總金額
    - 總訂單數：分析期間內的訂單數量
    - 客單價：總營收除以總訂單數
    - 估計淨利：扣除所有成本後的估計利潤（包含廣告費）
    
    **成本分析**
    - 估計進貨成本：可調整的進貨成本率（預設 50%）
    - 運費：根據運送方式自動計算的物流成本
    - 金流服務費：依付款方式計算的手續費
    - 廣告費：Meta 廣告平台的總支出
    - 營業稅：營收的 5%
    
    **廣告數據**
    - 總曝光：廣告的總曝光次數
    - 總點擊：廣告的總點擊次數
    - 點擊率：點擊數除以曝光數的百分比
    - ROAS：廣告投資報酬率（總營收/廣告費）
    
    **詳細數據分析**
    - 每日營收與成本：顯示每日營收及各項成本分解
    - 每日績效：營收、廣告支出和ROAS趨勢
    - 訂單明細：所有訂單的詳細資訊
    - 廣告績效：Meta廣告的詳細指標
    - 成本明細：各項成本的詳細計算
    
    **計算公式**
    - 估計淨利 = 總營收 - 估計進貨成本 - 運費 - 金流服務費 - 廣告費 - 營業稅
    - 總成本 = 估計進貨成本 + 運費 + 金流服務費 + 廣告費 + 營業稅
    
    **費率設定**
    - 運費：全家 $69、萊爾富 $58、宅配 $180
    - 金流服務費：超商取貨付款 0.53%、Line Pay 2.94%、信用卡 2.5725%
    - 營業稅：5%
    - 進貨成本率：可在側邊欄調整（預設 50%）
    """)

# 頁腳
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 1rem;'>
        <strong>電商業績分析儀表板</strong><br>
        專業電商數據分析平台 | 整合成本分析與獲利計算
    </div>
    """, unsafe_allow_html=True)