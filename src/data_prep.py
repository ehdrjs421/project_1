import pandas as pd
import numpy as np
from utils import helpers
import sys
import os

# def clean_data(df):
#     """
#     데이터 정제 작업을 수행합니다.
#     """
#     # TODO: Implement cleaning logic
#     return df

# def merge_datasets(*dfs):
#     """
#     여러 데이터셋을 병합합니다.
#     """
#     # TODO: Implement merge logic
#     return None
    
# root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# data_path = os.path.join(root_path,"project1","data","final_df_0121.csv")
# print(data_path)

# df = pd.read_csv(data_path)
# print(df['order_id'])

def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """
    orders 데이터 전처리:
    - datetime 변환
    - 배송 지연/총 배송일 계산
    - 배송 기간 구간화
    """
    orders = orders.copy()

    date_cols = [
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'order_purchase_timestamp'
    ]

    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    orders['delay_days'] = (
        orders['order_delivered_customer_date']
        - orders['order_estimated_delivery_date']
    )

    orders['total_delivery_time'] = (
        orders['order_delivered_customer_date']
        - orders['order_purchase_timestamp']
    )

    orders["total_day"] = pd.cut(
        orders["total_delivery_time"].dt.days,
        bins=[0, 5, 10, 15, 20, np.inf],
        labels=["0–5day", "5-10day", "10-15day", "15-20day", "20day+"],
        right=True
    )

    return orders.dropna()

def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    """
    product 데이터 정제:
    - 결측 제거
    - 치수 numeric 변환
    - 부피 계산
    """
    products = products.dropna().copy()

    cols = [
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]

    products[cols] = products[cols].apply(
        pd.to_numeric, errors='coerce'
    )

    products['product_volume'] = (
        products['product_length_cm']
        * products['product_height_cm']
        * products['product_width_cm']
    )

    return products


def merge_datasets(
    orders,
    order_items,
    order_reviews,
    customers,
    products,
    sellers
) -> pd.DataFrame:
    """
    모든 데이터셋 병합
    """
    merged = (
        orders
        .merge(order_items, on='order_id', how='left')
        .merge(order_reviews, on='order_id', how='left')
        .merge(customers, on='customer_id', how='left')
        .merge(products, on='product_id', how='left')
        .merge(sellers, on='seller_id', how='left')
    )

    return merged

def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        'customer_id','customer_zip_code_prefix','customer_state',
        'order_id','order_delivered_carrier_date',
        'order_purchase_timestamp','order_delivered_customer_date',
        'order_estimated_delivery_date','total_delivery_time',
        'delay_days','total_day',
        'order_item_id','product_id','seller_id',
        'price','freight_value','shipping_limit_date',
        'review_id','review_score','review_comment_message',
        'product_category_name','product_weight_g',
        'product_length_cm','product_height_cm',
        'product_width_cm','product_volume',
        'seller_zip_code_prefix','seller_state'
    ]
    return df[cols]

def save_dataframe(
    df: pd.DataFrame,
    root_path: str,
    filename: str = "final_df.csv"
) -> None:
    """
    최종 DataFrame을 data/final 경로에 저장합니다.
    """
    save_dir = os.path.join(root_path, "data", "final")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)
    df.to_csv(save_path, index=False, encoding="utf-8-sig")

    print(f"Final dataset saved to: {save_path}")
    
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data")

orders = pd.read_csv(os.path.join(data_path, "olist_orders_dataset.csv"))
order_items = pd.read_csv(os.path.join(data_path, "olist_order_items_dataset.csv"))
order_reviews = pd.read_csv(os.path.join(data_path, "olist_order_reviews_dataset.csv"))
customers = pd.read_csv(os.path.join(data_path, "olist_customers_dataset.csv"))
products = pd.read_csv(os.path.join(data_path, "olist_products_dataset.csv"))
sellers = pd.read_csv(os.path.join(data_path, "olist_sellers_dataset.csv"))

orders_clean = clean_orders(orders)
products_clean = clean_products(products)

total_df = merge_datasets(
    orders_clean,
    order_items,
    order_reviews,
    customers,
    products_clean,
    sellers
)

final_df = select_final_columns(total_df)

save_dataframe(
    final_df,
    root_path=data_path,
    filename="final_df.csv"
)