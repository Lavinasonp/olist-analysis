import pandas as pd
import numpy as np
import os
from src.config import PROCESSED_DATA_DIR

def load_processed_data(filename="master_table.parquet"):
    path = os.path.join(PROCESSED_DATA_DIR, filename)
    print(f"Loading {path}...")
    return pd.read_parquet(path)

def create_time_series_features(df):
    print("Starting Feature Engineering (Leakage-Free Version)...")
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    category_start_dates = df.groupby('product_category')['order_purchase_timestamp'].min().reset_index()
    category_start_dates.rename(columns={'order_purchase_timestamp': 'first_sale_date'}, inplace=True)

    weekly_data = df.groupby([
        'product_category', 
        pd.Grouper(key='order_purchase_timestamp', freq='W-MON')
    ]).agg(
        quantity_sold=('order_id', 'count'),
        revenue=('price', 'sum'),
        curr_avg_price=('price', 'mean'),
        curr_avg_freight=('freight_value', 'mean'),
        curr_active_sellers=('seller_id', 'nunique')
    ).reset_index()

    all_categories = weekly_data['product_category'].unique()
    all_weeks = weekly_data['order_purchase_timestamp'].unique()
    
    full_index = pd.MultiIndex.from_product(
        [all_categories, all_weeks], 
        names=['product_category', 'order_purchase_timestamp']
    )
    weekly_data = weekly_data.set_index(['product_category', 'order_purchase_timestamp'])
    weekly_data = weekly_data.reindex(full_index, fill_value=0).reset_index()
    
    weekly_data = pd.merge(weekly_data, category_start_dates, on='product_category', how='left')
    
    original_len = len(weekly_data)
    weekly_data = weekly_data[weekly_data['order_purchase_timestamp'] >= weekly_data['first_sale_date']].copy()
    print(f"Dropped {original_len - len(weekly_data)} rows of pre-launch data.")

    weekly_data = weekly_data.sort_values(['product_category', 'order_purchase_timestamp'])

    weekly_data['price_lag_1'] = weekly_data.groupby('product_category')['curr_avg_price'].shift(1)
    weekly_data['freight_lag_1'] = weekly_data.groupby('product_category')['curr_avg_freight'].shift(1)
    weekly_data['sellers_lag_1'] = weekly_data.groupby('product_category')['curr_active_sellers'].shift(1)
    
    weekly_data['price_lag_1'] = weekly_data.groupby('product_category')['price_lag_1'].ffill().fillna(0)
    weekly_data['freight_lag_1'] = weekly_data.groupby('product_category')['freight_lag_1'].ffill().fillna(0)
    weekly_data['sellers_lag_1'] = weekly_data['sellers_lag_1'].fillna(0)

    weekly_data['week_of_year'] = weekly_data['order_purchase_timestamp'].dt.isocalendar().week.astype(int)
    weekly_data['month'] = weekly_data['order_purchase_timestamp'].dt.month
    weekly_data['year'] = weekly_data['order_purchase_timestamp'].dt.year
    
    weekly_data['month_sin'] = np.sin(2 * np.pi * weekly_data['month']/12)
    weekly_data['month_cos'] = np.cos(2 * np.pi * weekly_data['month']/12)

    weekly_data['freight_ratio'] = weekly_data['freight_lag_1'] / weekly_data['price_lag_1']
    weekly_data['freight_ratio'] = weekly_data['freight_ratio'].fillna(0).replace([np.inf, -np.inf], 0)

    weekly_data['price_roll_mean_4'] = weekly_data.groupby('product_category')['price_lag_1'].transform(
        lambda x: x.rolling(window=4).mean()
    )
    weekly_data['price_momentum'] = weekly_data['price_lag_1'] / weekly_data['price_roll_mean_4']
    weekly_data['price_momentum'] = weekly_data['price_momentum'].fillna(1.0)

    lags = [1, 2, 3, 4, 8]
    for lag in lags:
        weekly_data[f'sales_lag_{lag}'] = weekly_data.groupby('product_category')['quantity_sold'].shift(lag)

    weekly_data['sales_roll_mean_4'] = weekly_data.groupby('product_category')['quantity_sold'].transform(
        lambda x: x.shift(1).rolling(window=4).mean()
    )
    
    weekly_data['sales_roll_std_4'] = weekly_data.groupby('product_category')['quantity_sold'].transform(
        lambda x: x.shift(1).rolling(window=4).std()
    )

    def get_weeks_to_bf(date):
        bf_date = pd.Timestamp(year=date.year, month=11, day=24)
        if date > bf_date:
            bf_date = pd.Timestamp(year=date.year + 1, month=11, day=24)
        delta = bf_date - date
        return int(delta.days / 7)

    weekly_data['weeks_to_bf'] = weekly_data['order_purchase_timestamp'].apply(get_weeks_to_bf)
    weekly_data['weeks_to_bf'] = weekly_data['weeks_to_bf'].clip(upper=20)
    
    weekly_data.dropna(inplace=True)
    
    drop_cols = ['revenue', 'curr_avg_price', 'curr_avg_freight', 'curr_active_sellers', 'first_sale_date']
    weekly_data.drop(columns=drop_cols, inplace=True)

    print(f"Feature Engineering Complete. Final Shape: {weekly_data.shape}")
    return weekly_data

def save_features(df, filename="features_v3.parquet"):
    path = os.path.join(PROCESSED_DATA_DIR, filename)
    print(f"Saving features to {path}...")
    df.to_parquet(path, index=False)
    print("Save complete.")

if __name__ == "__main__":
    df_raw = load_processed_data()
    df_feats = create_time_series_features(df_raw)
    save_features(df_feats)
