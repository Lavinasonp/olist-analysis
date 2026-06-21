import pandas as pd
import numpy as np
import joblib
import os
from src.config import PROCESSED_DATA_DIR, MODEL_DIR, REPORTS_DIR

def load_resources():
    print("Loading resources...")
    df = pd.read_parquet(os.path.join(PROCESSED_DATA_DIR, "features_v3.parquet"))
    model = joblib.load(os.path.join(MODEL_DIR, "lgbm_demand_v3.pkl"))
    return df, model

def generate_inventory_plan(service_level=0.95):
    print("Generating Inventory Plan...")
    df, model = load_resources()
    
    latest_date = df['order_purchase_timestamp'].max()
    print(f"Planning inventory based on data from week: {latest_date}")
    
    current_stock_data = df[df['order_purchase_timestamp'] == latest_date].copy()
    
    ignore_cols = ['order_purchase_timestamp', 'year', 'quantity_sold']
    features = [c for c in df.columns if c not in ignore_cols]
    
    current_stock_data['product_category'] = current_stock_data['product_category'].astype('category')
    
    X_pred = current_stock_data[features]
    
    predicted_demand = model.predict(X_pred)
    
    results = pd.DataFrame({
        'product_category': current_stock_data['product_category'],
        'predicted_weekly_demand': np.ceil(predicted_demand),
        'current_price': current_stock_data['price_lag_1'],
        'demand_std_dev': current_stock_data['sales_roll_std_4']
    })
    
    z_score = 1.645 if service_level == 0.95 else 1.28
    lead_time_weeks = 2
    
    results['demand_std_dev'] = results['demand_std_dev'].fillna(results['predicted_weekly_demand'])
    
    results['safety_stock'] = np.ceil(
        z_score * np.sqrt(lead_time_weeks) * results['demand_std_dev']
    )
    
    results['reorder_point'] = (results['predicted_weekly_demand'] * lead_time_weeks) + results['safety_stock']
    
    results['order_recommendation'] = results['reorder_point'].apply(lambda x: f"Maintain ~{int(x)} units")
    
    results = results.sort_values('predicted_weekly_demand', ascending=False)
    
    save_path = os.path.join(REPORTS_DIR, "inventory_replenishment_plan.csv")
    results.to_csv(save_path, index=False)
    
    print("\n--- INVENTORY REPLENISHMENT PLAN (Top 5 Categories) ---")
    print(results[['product_category', 'predicted_weekly_demand', 'demand_std_dev', 'safety_stock', 'reorder_point']].head(5))
    print(f"\nFull plan saved to {save_path}")

if __name__ == "__main__":
    generate_inventory_plan()
