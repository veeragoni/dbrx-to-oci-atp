#!/usr/bin/env python3
"""Simple Delta Sharing test"""

import delta_sharing
import json

# Create profile
profile = {
    "shareCredentialsVersion": 1,
    "endpoint": "https://sharing.delta.io/delta-sharing/",
    "bearerToken": "faaie590d541265bcab1f2de9813274bf233"
}

with open('demo.share', 'w') as f:
    json.dump(profile, f, indent=2)

print("Testing Delta Sharing...")

# Load small dataset
table_url = "demo.share#delta_sharing.default.boston-housing"
df = delta_sharing.load_as_pandas(table_url, limit=10)

print(f"Loaded {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")
print("\nSample data:")
print(df.head(3))
print("\n✅ Delta Sharing works!")
