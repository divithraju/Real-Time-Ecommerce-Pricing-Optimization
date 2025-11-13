# Ecommerce Pricing Optimization - Production-ready Demo

This project provides a production-grade architecture for pricing optimization including:
- API ingestion (simulated)
- Spark ETL
- Spark MLlib training & MLflow tracking
- Batch scoring
- Airflow orchestration
- Sqoop for legacy MySQL import

## Key points
- ML training uses Spark MLlib with CrossValidator and logs to MLflow. Update `config/pipeline_config.yaml` with your MLflow server.
- Replace simulated ingestion with real API calls and set PRODUCT_API_KEY in your environment.
- For production, run Spark jobs on YARN/cluster and point paths to HDFS (config contains placeholders).

## Quick demo steps (local)
1. Install required Python packages: `pip install mlflow pandas pyarrow fastparquet joblib scikit-learn requests`
2. Generate input data:
   `python3 ingestion/fetch_products.py` (writes data/input/product_pricing.csv)
   `python3 ingestion/fetch_api_simulated.py` (if you have it) or ensure sales_transactions_simulated.csv exists
3. Run ETL:
   `spark-submit --master local[*] spark_transform/sales_transform_job.py`
4. Train model (requires MLflow server configured):
   `spark-submit --master local[*] spark_ml/train_pricing_model.py`
5. Score:
   `spark-submit --master local[*] spark_ml/batch_score.py`
6. Validate:
   `python3 validation/data_quality_check.py`

## Security
- Use `.env` or secrets manager for API keys and DB creds. See `.env.example`.

## Author
Divith Raju
