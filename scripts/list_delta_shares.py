#!/usr/bin/env python3
"""
List available shares, schemas, and tables from Delta Share
"""
import delta_sharing

# Use the demo.share profile
profile_path = "demo.share"

print("Loading Delta Share profile...")
client = delta_sharing.SharingClient(profile_path)

# List all shares
print("\n=== Available Shares ===")
shares = client.list_shares()
for share in shares:
    print(f"  - {share.name}")

    # List schemas in each share
    print(f"\n    Schemas in '{share.name}':")
    schemas = client.list_schemas(share)
    for schema in schemas:
        print(f"      - {schema.name}")

        # List tables in each schema
        print(f"        Tables in '{schema.name}':")
        tables = client.list_tables(schema)
        for table in tables:
            print(f"          - {table.name}")
            print(f"            Full path: {share.name}.{schema.name}.{table.name}")
    print()

print("\n=== Summary ===")
print("Use one of the full paths above in your test_function.py")
print("Format: share_name.schema_name.table_name")
