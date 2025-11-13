#!/usr/bin/env python3
import yaml, os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, avg, sum as _sum, year, month

cfg = yaml.safe_load(open('config/pipeline_config.yaml'))
def get_spark():
    return SparkSession.builder.appName(cfg['spark']['app_name']).getOrCreate()

def main():
    spark = get_spark()
    # local demo paths
    prod = spark.read.option('header',True).csv('data/input/product_pricing.csv')
    sales = spark.read.option('header',True).csv('data/input/sales_transactions_simulated.csv')
    prod = prod.withColumn('product_id', col('product_id').cast('int')).withColumn('price_usd', col('price_usd').cast('double')).withColumn('discount_pct', col('discount_pct').cast('double'))
    sales = sales.withColumn('product_id', col('product_id').cast('int')).withColumn('amount', col('amount').cast('double'))
    joined = sales.join(prod, on='product_id', how='left')
    joined = joined.withColumn('year', year(col('last_updated'))).withColumn('month', month(col('last_updated')))
    joined = joined.withColumn('price_after_discount', round(col('price_usd') * (1 - col('discount_pct')/100.0),2))
    agg = joined.groupBy('category','region','year','month').agg(_sum('amount').alias('total_sales'), round(avg('amount'),2).alias('avg_sales'), round(avg('price_after_discount'),2).alias('avg_discounted_price'))
    os.makedirs('data/output', exist_ok=True)
    agg.coalesce(1).write.mode('overwrite').parquet('data/output/pricing_aggregates.parquet')
    joined.coalesce(1).write.mode('overwrite').parquet('data/output/joined_transactions.parquet')
    spark.stop()

if __name__=='__main__':
    main()
