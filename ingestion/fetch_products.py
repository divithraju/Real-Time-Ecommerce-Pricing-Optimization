#!/usr/bin/env python3
"""Ingestion module: fetches product & currency data.
Replace simulate() with real requests when you have API access."""
import os, csv, random
from datetime import datetime, timedelta

OUT_DIR = os.path.join('data','input')
os.makedirs(OUT_DIR, exist_ok=True)

def simulate_products(n=150):
    categories = ['Electronics','Apparel','Grocery','Home','Sports','Beauty']
    brands = ['BrandA','BrandB','BrandC']
    rows = []
    base = datetime.utcnow()
    for i in range(1, n+1):
        rows.append({
            'product_id': i,
            'sku': f'SKU{i:05d}',
            'product_name': f'Product-{i}',
            'brand': random.choice(brands),
            'category': random.choice(categories),
            'price_usd': round(random.uniform(50,2000),2),
            'discount_pct': round(random.uniform(0,40),2),
            'timestamp': (base - timedelta(days=random.randint(0,30))).strftime('%Y-%m-%d %H:%M:%S')
        })
    return rows

def save_products(rows, path):
    keys = ['product_id','sku','product_name','brand','category','price_usd','discount_pct','timestamp']
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('Wrote', path)

def main():
    prods = simulate_products(150)
    save_products(prods, os.path.join(OUT_DIR,'product_pricing.csv'))

if __name__=='__main__':
    main()
