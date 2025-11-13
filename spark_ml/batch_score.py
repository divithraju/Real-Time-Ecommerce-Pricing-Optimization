#!/usr/bin/env python3
"""Batch scoring: loads a registered MLflow model (Spark) and scores new processed data, writes results to parquet/Hive."""
import yaml, mlflow
from pyspark.sql import SparkSession
cfg = yaml.safe_load(open('config/pipeline_config.yaml'))
spark = SparkSession.builder.appName(cfg['spark']['app_name']).getOrCreate()
mlflow.set_tracking_uri(cfg['mlflow']['tracking_uri'])


local_processed = 'data/output/pricing_aggregates.parquet'
model_uri = cfg['mlflow'].get('model_registry_uri', None) or 'models:/%s/Production' % cfg['mlflow']['model_registry']

def main():
    df = spark.read.parquet(local_processed)
    # Load model from registry 
    try:
        model = mlflow.spark.load_model(model_uri)
        scored = model.transform(df)
        scored.select('*').write.mode('overwrite').parquet('data/output/scored_pricing.parquet')
        print('Scoring complete - wrote data/output/scored_pricing.parquet')
    except Exception as e:
        print('Model load/score failed (registry may be empty):', e)
    finally:
        spark.stop()

if __name__=='__main__':
    main()
