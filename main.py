import sys
import os

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_and_merge_data, save_processed
from src.preprocessing import load_processed_data, create_time_series_features, save_features
from src.training import train_model
from src.evaluation import generate_report
from src.inventory import generate_inventory_plan

def main():
    print("Starting Olist Supply Chain Pipeline (E2E)")

    print("\nLoading and Merging Raw Data...")
    try:
        df_master = load_and_merge_data()
        save_processed(df_master)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure your CSV files are in 'data/raw/'")
        return

    print("\nFeature Engineering (V3)...")
    df_raw = load_processed_data("master_table.parquet")
    df_feats = create_time_series_features(df_raw)
    save_features(df_feats, "features_v3.parquet")

    print("\nModel Training...")
    train_model()

    print("\nGenerating Reports...")
    generate_report()

    print("\nGenerating Inventory Plan...")
    generate_inventory_plan(service_level=0.95)

    print("\nPipeline Complete Successfully.")
    print("Check 'reports/' for graphs and inventory plans.")

if __name__ == "__main__":
    main()