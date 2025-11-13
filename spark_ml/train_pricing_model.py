#!/usr/bin/env python3
"""Spark MLlib training pipeline for pricing optimization.
Reads processed parquet data, trains a GBTRegressor, logs to MLflow, and saves model to HDFS.
"""
import os, yaml, mlflow, mlflow.spark
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

cfg = yaml.safe_load(open('config/pipeline_config.yaml'))
spark = SparkSession.builder.appName(cfg['spark']['app_name']).getOrCreate()

# Paths
processed_path = cfg['processed_path']  # hdfs path in production
# For demo/local, use local data/output
local_processed = 'data/output/pricing_aggregates.parquet'

# MLflow settings
mlflow.set_tracking_uri(cfg['mlflow']['tracking_uri'])
mlflow.set_experiment(cfg['mlflow']['experiment_name'])

def load_data(path):
    # uses local parquet for demo; change to Spark HDFS paths in production
    df = spark.read.parquet(path)
    return df

def build_pipeline(cat_cols, num_cols, label_col):
    stages = []
    indexers = [StringIndexer(inputCol=c, outputCol=c+'_idx', handleInvalid='keep') for c in cat_cols]
    encoders = [OneHotEncoder(inputCols=[c+'_idx'], outputCols=[c+'_ohe']) for c in cat_cols]
    stages += indexers + encoders
    assembler = VectorAssembler(inputCols=[c+'_ohe' for c in cat_cols] + num_cols, outputCol='features_raw')
    scaler = StandardScaler(inputCol='features_raw', outputCol='features')
    stages += [assembler, scaler]
    gbt = GBTRegressor(featuresCol='features', labelCol=label_col, maxIter=100)
    stages.append(gbt)
    pipeline = Pipeline(stages=stages)
    return pipeline, gbt

def main():
    df = load_data(local_processed)
    # Expect columns: category, region, year, month, total_sales, avg_sales, avg_discounted_price
    df = df.na.drop(subset=['total_sales','avg_sales'])
    cat_cols = ['category','region']
    num_cols = ['avg_sales','avg_discounted_price']
    label = 'total_sales'
    pipeline, gbt = build_pipeline(cat_cols, num_cols, label)
    paramGrid = ParamGridBuilder().addGrid(gbt.maxDepth, [5,8]).addGrid(gbt.maxIter, [50,100]).build()
    evaluator = RegressionEvaluator(labelCol=label, predictionCol='prediction', metricName='rmse')
    cv = CrossValidator(estimator=pipeline, estimatorParamMaps=paramGrid, evaluator=evaluator, numFolds=3, parallelism=2)
    with mlflow.start_run(run_name='spark_gbt_training'):
        model = cv.fit(df)
        best_model = model.bestModel
        # evaluate on training data (for demo)
        preds = best_model.transform(df)
        rmse = evaluator.evaluate(preds)
        mlflow.log_metric('rmse', float(rmse))
        # log model to mlflow and save to HDFS path
        model_uri = 'models:/%s/%s' % (cfg['mlflow']['model_registry'], 'v1-demo')
        mlflow.spark.log_model(best_model, artifact_path='spark-model', registered_model_name=cfg['mlflow']['model_registry'])
        print('Training complete. RMSE:', rmse)

if __name__ == '__main__':
    main()
