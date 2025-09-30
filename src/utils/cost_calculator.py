# cost_calculator.py - 成本計算工具
"""
這個模組負責計算各種成本，包括：
- 運費計算
- 金流手續費計算
- 進貨成本計算
- 營業稅計算
"""

import pandas as pd
from typing import Dict, Tuple
from src.constants import SHIPPING_COSTS, PAYMENT_FEES, TAX_RATE


def calculate_shipping_costs(shipping_methods: Dict[str, int]) -> Tuple[Dict, float]:
    """
    計算運費

    Args:
        shipping_methods: 運送方式及訂單數量的字典 {"方式": 數量}

    Returns:
        (shipping_costs_detail, total_shipping_cost)
        - shipping_costs_detail: 詳細的運費資訊
        - total_shipping_cost: 總運費
    """
    shipping_costs = {}
    total_shipping_cost = 0

    for method, count in shipping_methods.items():
        cost_per_order = 0

        # 模糊匹配運送方式
        for key, cost in SHIPPING_COSTS.items():
            if key.lower() in method.lower() or method.lower() in key.lower():
                cost_per_order = cost
                break

        total_cost = cost_per_order * count
        shipping_costs[method] = {
            'count': count,
            'cost_per_order': cost_per_order,
            'total_cost': total_cost
        }
        total_shipping_cost += total_cost

    return shipping_costs, total_shipping_cost


def calculate_payment_fees(orders_df: pd.DataFrame) -> Tuple[Dict, float]:
    """
    計算金流手續費

    Args:
        orders_df: 訂單 DataFrame，必須包含 'payment_method' 和 'total' 欄位

    Returns:
        (payment_fees_detail, total_payment_fee)
        - payment_fees_detail: 詳細的手續費資訊
        - total_payment_fee: 總手續費
    """
    payment_fees = {}
    total_payment_fee = 0

    if not orders_df.empty:
        # 按付款方式分組統計
        payment_summary = orders_df.groupby('payment_method').agg({
            'total': ['count', 'sum']
        }).round(2)
        payment_summary.columns = ['order_count', 'total_amount']
        payment_summary = payment_summary.reset_index()

        for _, row in payment_summary.iterrows():
            method = row['payment_method']
            count = int(row['order_count'])
            amount = float(row['total_amount'])

            # 模糊匹配付款方式的手續費率
            fee_rate = 0.0
            for key, rate in PAYMENT_FEES.items():
                if key.lower() in method.lower() or method.lower() in key.lower():
                    fee_rate = rate
                    break

            fee_amount = amount * (fee_rate / 100)
            payment_fees[method] = {
                'count': count,
                'total_amount': amount,
                'fee_rate': fee_rate,
                'fee_amount': fee_amount
            }
            total_payment_fee += fee_amount

    return payment_fees, total_payment_fee


def calculate_cogs(revenue: float, cogs_rate: float) -> float:
    """
    計算進貨成本 (Cost of Goods Sold)

    Args:
        revenue: 總營收
        cogs_rate: 進貨成本率 (百分比，如 50 代表 50%)

    Returns:
        進貨成本金額
    """
    return revenue * (cogs_rate / 100)


def calculate_business_tax(revenue: float, tax_rate: float = TAX_RATE) -> float:
    """
    計算營業稅

    Args:
        revenue: 總營收
        tax_rate: 稅率 (預設使用 constants.TAX_RATE)

    Returns:
        營業稅金額
    """
    return revenue * tax_rate


def calculate_net_profit(revenue: float, cogs: float, shipping_cost: float,
                        payment_fee: float, ad_spend: float, business_tax: float) -> float:
    """
    計算淨利

    Args:
        revenue: 總營收
        cogs: 進貨成本
        shipping_cost: 運費
        payment_fee: 金流手續費
        ad_spend: 廣告費
        business_tax: 營業稅

    Returns:
        淨利金額
    """
    total_costs = cogs + shipping_cost + payment_fee + ad_spend + business_tax
    return revenue - total_costs


def calculate_total_costs(cogs: float, shipping_cost: float, payment_fee: float,
                         ad_spend: float, business_tax: float) -> float:
    """
    計算總成本

    Args:
        cogs: 進貨成本
        shipping_cost: 運費
        payment_fee: 金流手續費
        ad_spend: 廣告費
        business_tax: 營業稅

    Returns:
        總成本金額
    """
    return cogs + shipping_cost + payment_fee + ad_spend + business_tax