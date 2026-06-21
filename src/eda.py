import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from src.config import PROCESSED_DATA_DIR, REPORTS_DIR, RAW_DATA_DIR

FIGURES_DIR = os.path.join(REPORTS_DIR, "eda_visuals")
os.makedirs(FIGURES_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk", palette="viridis")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12

def load_master_data():
    path = os.path.join(PROCESSED_DATA_DIR, "master_table.parquet")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run src/data_loader.py first.")
    df = pd.read_parquet(path)
    date_cols = ['order_purchase_timestamp', 'order_approved_at', 
                 'order_delivered_carrier_date', 'order_delivered_customer_date', 
                 'order_estimated_delivery_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def plot_basic_trends(df):
    print("Generating Basic Trends...")
    monthly_sales = df.set_index('order_purchase_timestamp').resample('M')['price'].sum()
    plt.figure()
    monthly_sales.plot(kind='line', linewidth=3, marker='o', color='#2ecc71')
    plt.title('Total Monthly Revenue', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "01_monthly_revenue.png"))
    plt.close()

def plot_delay_analysis(df):
    print("Generating Delay Analysis...")
    
    df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    df['is_late'] = df['delay_days'] > 0
    
    plot_data = df[(df['delay_days'] > -20) & (df['delay_days'] < 20)]
    state_order = plot_data.groupby('customer_state')['delay_days'].median().sort_values(ascending=False).index
    
    plt.figure(figsize=(16, 8))
    sns.boxplot(data=plot_data, x='customer_state', y='delay_days', order=state_order, palette='RdBu_r')
    plt.axhline(0, color='black', linestyle='--', linewidth=2, label='On Time')
    plt.title('Delivery Reliability by State (Actual vs Estimated)', fontweight='bold')
    plt.ylabel('Days Late (Positive) or Early (Negative)')
    plt.xlabel('State')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "07_state_delay_distribution.png"))
    plt.close()

    late_metrics = df.groupby('customer_state')['is_late'].mean().sort_values(ascending=False).reset_index()
    late_metrics['is_late'] = late_metrics['is_late'] * 100 
    
    plt.figure(figsize=(16, 8))
    sns.barplot(data=late_metrics, x='customer_state', y='is_late', palette='magma')
    plt.title('Percentage of Orders Delivered Late per State', fontweight='bold')
    plt.ylabel('% Late Orders')
    plt.axhline(late_metrics['is_late'].mean(), color='red', linestyle='--', label='National Average')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "08_percent_late_by_state.png"))
    plt.close()

def plot_city_analysis(df):
    print("Generating City Analysis...")
    
    top_cities = df['customer_city'].value_counts().head(20).index
    city_df = df[df['customer_city'].isin(top_cities)].copy()
    city_df['delivery_time'] = (city_df['order_delivered_customer_date'] - city_df['order_purchase_timestamp']).dt.days
    order = city_df.groupby('customer_city')['delivery_time'].mean().sort_values(ascending=False).index
    
    plt.figure(figsize=(16, 10))
    sns.barplot(data=city_df, y='customer_city', x='delivery_time', order=order, palette='cool_r')
    plt.title('Average Delivery Time (Days) - Top 20 Cities', fontweight='bold')
    plt.xlabel('Days')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "09_city_delivery_speed.png"))
    plt.close()

def plot_buying_heatmap(df):
    print("Generating Buying Pattern Heatmap...")
    
    df['hour'] = df['order_purchase_timestamp'].dt.hour
    df['day_of_week'] = df['order_purchase_timestamp'].dt.day_name()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack()
    heatmap_data = heatmap_data.reindex(days_order)
    
    plt.figure(figsize=(16, 8))
    sns.heatmap(heatmap_data, cmap='YlGnBu', annot=False, fmt='d')
    plt.title('Heatmap of Orders: Day vs Hour', fontweight='bold')
    plt.xlabel('Hour of Day (0-23)')
    plt.ylabel('Day of Week')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "10_buying_heatmap.png"))
    plt.close()

def plot_payment_stats():
    try:
        path = os.path.join(RAW_DATA_DIR, "olist_order_payments_dataset.csv")
        if os.path.exists(path):
            payments = pd.read_csv(path)
            payment_counts = payments['payment_type'].value_counts()
            
            plt.figure(figsize=(10, 10))
            plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
            plt.title('Distribution of Payment Methods', fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(FIGURES_DIR, "11_payment_methods.png"))
            plt.close()
    except Exception as e:
        print(f"Skipping payment analysis: {e}")

def plot_logistics_breakdown(df):
    print("Generating Logistics Breakdown...")
    
    df['time_to_ship'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.days
    df['carrier_time'] = (df['order_delivered_customer_date'] - df['order_delivered_carrier_date']).dt.days
    
    valid_logistics = df[
        (df['time_to_ship'] >= 0) & 
        (df['carrier_time'] >= 0) & 
        (df['time_to_ship'] < 30) & 
        (df['carrier_time'] < 60)
    ].copy()
    
    plt.figure(figsize=(14, 7))
    sns.histplot(valid_logistics['time_to_ship'], color='#3498db', alpha=0.6, label='Seller Processing Time', bins=20, kde=True)
    sns.histplot(valid_logistics['carrier_time'], color='#e67e22', alpha=0.6, label='Carrier Transit Time', bins=40, kde=True)
    plt.title('Global Speed Comparison: Seller vs. Carrier', fontweight='bold')
    plt.xlabel('Days')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "12_seller_vs_carrier_hist.png"))
    plt.close()

    print("Generating State-wise Logistics Stacked Bar...")
    
    state_logs = valid_logistics.groupby('customer_state')[['time_to_ship', 'carrier_time']].mean().sort_values('carrier_time', ascending=False)
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar(state_logs.index, state_logs['time_to_ship'], label='Seller Processing', color='#3498db', alpha=0.8)
    ax.bar(state_logs.index, state_logs['carrier_time'], bottom=state_logs['time_to_ship'], label='Carrier Transit', color='#e67e22', alpha=0.8)
    
    # Formatting
    plt.title('Average Delivery Composition by State (Who is the bottleneck?)', fontweight='bold')
    plt.ylabel('Average Days')
    plt.xlabel('Customer State')
    plt.legend()
    
    for i, state in enumerate(state_logs.index):
        total = state_logs.loc[state, 'time_to_ship'] + state_logs.loc[state, 'carrier_time']
        ax.text(i, total + 0.5, f"{total:.1f}", ha='center', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "13_state_logistics_breakdown.png"))
    plt.close()


if __name__ == "__main__":
    df_master = load_master_data()
    plot_basic_trends(df_master)
    plot_delay_analysis(df_master)
    plot_city_analysis(df_master)
    plot_buying_heatmap(df_master)
    plot_payment_stats()
    plot_logistics_breakdown(df_master)
    
    print(f"\nAll plots (including state logistics) saved to: {FIGURES_DIR}")
