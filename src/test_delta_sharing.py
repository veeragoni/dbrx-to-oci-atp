#!/usr/bin/env python3
"""
Test script for Delta Sharing using public demo shares
"""

import delta_sharing

# Public Delta Sharing endpoint (Databricks demo)
profile_file = {
    "shareCredentialsVersion": 1,
    "endpoint": "https://sharing.delta.io/delta-sharing/",
    "bearerToken": "faaie590d541265bcab1f2de9813274bf233"
}

# Save profile to file
import json
with open('demo.share', 'w') as f:
    json.dump(profile_file, f, indent=2)

print("Testing Delta Sharing with public demo data...\n")

# Create client
client = delta_sharing.SharingClient("demo.share")

# List all shares
print("Available shares:")
shares = client.list_shares()
for share in shares:
    print(f"  - {share.name}")

print("\nAvailable schemas in delta_sharing:")
schemas = client.list_schemas(shares[0])
for schema in schemas:
    print(f"  - {schema.name}")

print("\nAvailable tables in delta_sharing.default:")
tables = client.list_tables(schemas[0])
for table in tables:
    print(f"  - {table.name}")

# Load COVID-19 data
print("\n" + "="*60)
print("Loading COVID-19 NYT data sample...")
print("="*60)

table_url = "demo.share#delta_sharing.default.COVID_19_NYT"
df = delta_sharing.load_as_pandas(table_url)

print(f"\nTotal rows: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(df.head())

print("\n" + "="*60)
print("Loading Boston Housing data sample...")
print("="*60)

table_url = "demo.share#delta_sharing.default.boston-housing"
df2 = delta_sharing.load_as_pandas(table_url)

print(f"\nTotal rows: {len(df2)}")
print(f"\nColumns: {df2.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(df2.head())

print("\n✅ Delta Sharing is working correctly!")
print("\nCleanup: You can delete 'demo.share' file when done testing.")
