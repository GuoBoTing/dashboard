# woocommerce.py - WooCommerce API 客戶端
"""
WooCommerce REST API 客戶端模組
負責從 WooCommerce 商店獲取訂單數據
"""

import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from typing import Tuple, Dict
from src.constants import WC_API_VERSION, WC_MAX_ORDERS_PER_PAGE, WC_MAX_ORDERS_TOTAL


class WooCommerceAPI:
    """WooCommerce API 客戶端"""

    def __init__(self, url: str, consumer_key: str, consumer_secret: str):
        """
        初始化 WooCommerce API 客戶端

        Args:
            url: WooCommerce 商店網址
            consumer_key: Consumer Key
            consumer_secret: Consumer Secret
        """
        self.url = url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.auth = HTTPBasicAuth(consumer_key, consumer_secret)
        self.endpoint = f"{self.url}/wp-json/wc/{WC_API_VERSION}/orders"

    def get_orders(self, start_date: datetime, end_date: datetime,
                   status: str = 'completed,processing,on-hold,wmp-in-transit,wmp-shipped,ry-at-cvs') -> Tuple[pd.DataFrame, Dict, Dict]:
        """
        獲取訂單數據

        Args:
            start_date: 開始日期
            end_date: 結束日期
            status: 訂單狀態（逗號分隔），預設包含標準狀態和自訂狀態

        Returns:
            (orders_df, payment_methods, shipping_methods)
            - orders_df: 訂單 DataFrame
            - payment_methods: 付款方式統計
            - shipping_methods: 運送方式統計
        """
        try:
            params = {
                'after': start_date.strftime('%Y-%m-%d') + 'T00:00:00',
                'before': end_date.strftime('%Y-%m-%d') + 'T23:59:59',
                'per_page': WC_MAX_ORDERS_PER_PAGE,
                'status': status,
                'orderby': 'date',
                'order': 'desc'
            }

            with st.spinner("正在獲取 WooCommerce 數據..."):
                all_orders = []
                page = 1

                # 分頁獲取訂單
                while True:
                    params['page'] = page
                    response = requests.get(
                        self.endpoint,
                        auth=self.auth,
                        params=params,
                        timeout=30
                    )

                    if response.status_code == 200:
                        orders = response.json()
                        if not orders:
                            break

                        all_orders.extend(orders)
                        page += 1

                        # 限制最大訂單數
                        if len(all_orders) >= WC_MAX_ORDERS_TOTAL:
                            break
                    else:
                        if page == 1:
                            st.error(f"WooCommerce API 錯誤: {response.text}")
                            return pd.DataFrame(), {}, {}
                        else:
                            break

                # 處理訂單數據
                order_data = []
                payment_methods = {}
                shipping_methods = {}

                for order in all_orders:
                    # 基本訂單資訊
                    order_info = {
                        'order_id': order['id'],
                        'date': pd.to_datetime(order['date_created']).date(),
                        'total': float(order['total']),
                        'status': order['status'],
                        'customer_id': order.get('customer_id', 0),
                        'payment_method': order.get('payment_method_title', '未知'),
                        'shipping_method': '未知'
                    }

                    # 統計付款方式
                    payment_method = order.get('payment_method_title', '未知')
                    payment_methods[payment_method] = payment_methods.get(payment_method, 0) + 1

                    # 統計運送方式
                    shipping_lines = order.get('shipping_lines', [])
                    if shipping_lines:
                        shipping_method = shipping_lines[0].get('method_title', '未知')
                        order_info['shipping_method'] = shipping_method
                        shipping_methods[shipping_method] = shipping_methods.get(shipping_method, 0) + 1
                    else:
                        shipping_methods['未知'] = shipping_methods.get('未知', 0) + 1

                    order_data.append(order_info)

                # 轉換為 DataFrame
                df = pd.DataFrame(order_data)
                st.success(f"成功獲取 {len(all_orders)} 筆 WooCommerce 訂單")

                return df, payment_methods, shipping_methods

        except Exception as e:
            st.error(f"WooCommerce 連接錯誤: {str(e)}")
            return pd.DataFrame(), {}, {}

    def test_connection(self) -> bool:
        """
        測試 API 連接

        Returns:
            True if connection successful, False otherwise
        """
        try:
            params = {'per_page': 1}
            response = requests.get(
                self.endpoint,
                auth=self.auth,
                params=params,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False


def get_woocommerce_data(url: str, consumer_key: str, consumer_secret: str,
                        start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, Dict, Dict]:
    """
    便捷函數：獲取 WooCommerce 數據

    Args:
        url: WooCommerce 商店網址
        consumer_key: Consumer Key
        consumer_secret: Consumer Secret
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        (orders_df, payment_methods, shipping_methods)
    """
    api_client = WooCommerceAPI(url, consumer_key, consumer_secret)
    return api_client.get_orders(start_date, end_date)