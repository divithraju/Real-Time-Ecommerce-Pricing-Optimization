#!/usr/bin/env python3
import os, json
from datetime import datetime
REPORT_DIR = 'data/validation'
os.makedirs(REPORT_DIR, exist_ok=True)
report = {
    'timestamp': datetime.utcnow().isoformat(),
    'product_pricing_exists': os.path.exists('data/input/product_pricing.csv'),
    'sales_transactions_exists': os.path.exists('data/input/sales_transactions_simulated.csv'),
    'aggregates_exists': os.path.exists('data/output/pricing_aggregates.parquet'),
}
with open(os.path.join(REPORT_DIR, 'dq_report.json'),'w') as f:
    json.dump(report, f, indent=2)
print('Validation report saved to data/validation/dq_report.json')
