import pandas as pd
import os
import streamlit as st
import numpy as np

@st.cache_data
def load_data():
    master_path = os.path.join("Data", "processed", "master_table.parquet")
    if not os.path.exists(master_path):
        st.error(f"Missing {master_path}. Please run data_loader.py")
        st.stop()
        
    df_master = pd.read_parquet(master_path)
    
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at', 
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        df_master[col] = pd.to_datetime(df_master[col], errors='coerce')
        
    df_master['time_to_ship'] = (df_master['order_delivered_carrier_date'] - df_master['order_approved_at']).dt.days
    df_master['carrier_time'] = (df_master['order_delivered_customer_date'] - df_master['order_delivered_carrier_date']).dt.days
    df_master['delay_days'] = (df_master['order_delivered_customer_date'] - df_master['order_estimated_delivery_date']).dt.days
    df_master['is_late'] = (df_master['delay_days'] > 0).astype(int)
    
    df_master['order_month'] = df_master['order_purchase_timestamp'].dt.to_period('M').astype(str)
    df_master['order_day_of_week'] = df_master['order_purchase_timestamp'].dt.day_name()
    df_master['order_hour'] = df_master['order_purchase_timestamp'].dt.hour
    
    df_master['freight_ratio'] = (df_master['freight_value'] / df_master['price']) * 100
    df_master['freight_ratio'] = df_master['freight_ratio'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    return df_master

def get_executive_metrics(df):
    total_revenue = df['price'].sum()
    total_orders = df['order_id'].nunique()
    total_customers = df['customer_id'].nunique()
    avg_order_value = df['price'].mean()
    
    return total_revenue, total_orders, total_customers, avg_order_value

def get_logistics_metrics(df):
    valid_logs = df[(df['time_to_ship'] >= 0) & (df['carrier_time'] >= 0)].copy()
    avg_seller_processing = valid_logs['time_to_ship'].mean()
    avg_carrier_transit = valid_logs['carrier_time'].mean()
    late_pct = valid_logs['is_late'].mean() * 100
    
    return avg_seller_processing, avg_carrier_transit, late_pct, valid_logs

def get_freight_metrics(df):
    avg_freight = df['freight_value'].mean()
    avg_freight_ratio = df['freight_ratio'].mean()
    return avg_freight, avg_freight_ratio
