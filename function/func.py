import io
import json
import logging
import os

try:
    from fdk import response
    import delta_sharing
    import oracledb
    import pandas as pd
except ImportError as e:
    # Log import errors for debugging
    import sys
    sys.stderr.write(f"Import error: {str(e)}\n")
    raise

def handler(ctx, data: io.BytesIO = None):
    """
    OCI Function handler to migrate data from Databricks Delta Share to Oracle ATP

    Expected input JSON:
    {
        "delta_profile_base64": "base64 encoded delta share profile content",
        "share_name": "share_name",
        "schema_name": "schema_name",
        "table_name": "table_name",
        "oracle_user": "ADMIN",
        "oracle_password": "password",
        "oracle_dsn": "connection_string",
        "oracle_wallet_location": "/tmp/wallet",
        "oracle_wallet_password": null,
        "batch_size": 100,
        "limit_rows": null
    }
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        # Parse input
        body = json.loads(data.getvalue()) if data.getvalue() else {}
        logger.info(f"Received request with keys: {body.keys()}")

        # Extract parameters
        delta_profile_b64 = body.get("delta_profile_base64")
        share_name = body.get("share_name")
        schema_name = body.get("schema_name")
        table_name = body.get("table_name")
        oracle_user = body.get("oracle_user")
        oracle_password = body.get("oracle_password")
        oracle_dsn = body.get("oracle_dsn")
        oracle_wallet_location = body.get("oracle_wallet_location")
        oracle_wallet_password = body.get("oracle_wallet_password")
        batch_size = body.get("batch_size", 100)
        limit_rows = body.get("limit_rows")
        oracle_table_name = body.get("oracle_table_name", table_name)

        # Validate required parameters
        required_params = {
            "delta_profile_base64": delta_profile_b64,
            "share_name": share_name,
            "schema_name": schema_name,
            "table_name": table_name,
            "oracle_user": oracle_user,
            "oracle_password": oracle_password,
            "oracle_dsn": oracle_dsn
        }

        missing = [k for k, v in required_params.items() if not v]
        if missing:
            return response.Response(
                ctx,
                response_data=json.dumps({"error": f"Missing required parameters: {missing}"}),
                headers={"Content-Type": "application/json"},
                status_code=400
            )

        # Decode and save delta profile
        import base64
        profile_content = base64.b64decode(delta_profile_b64).decode('utf-8')
        profile_path = "/tmp/delta.share"
        with open(profile_path, 'w') as f:
            f.write(profile_content)

        logger.info(f"Loading data from Delta Share: {share_name}.{schema_name}.{table_name}")

        # Load data from Delta Share
        table_url = f"{profile_path}#{share_name}.{schema_name}.{table_name}"
        df = delta_sharing.load_as_pandas(table_url, limit=limit_rows)
        total_rows = len(df)

        logger.info(f"Loaded {total_rows} rows from Delta Share")

        # Connect to Oracle ATP
        logger.info("Connecting to Oracle ATP")
        oracle_conn = get_oracle_connection(
            oracle_user, oracle_password, oracle_dsn,
            oracle_wallet_location, oracle_wallet_password
        )
        oracle_cursor = oracle_conn.cursor()

        # Get DataFrame columns and types
        columns = df.columns.tolist()

        # Check if table exists, create if not
        logger.info(f"Checking if table {oracle_table_name} exists")
        try:
            oracle_cursor.execute(f"SELECT COUNT(*) FROM {oracle_table_name} WHERE ROWNUM = 1")
            # Table exists, truncate it
            logger.info(f"Table exists, truncating {oracle_table_name}")
            oracle_cursor.execute(f"TRUNCATE TABLE {oracle_table_name}")
            logger.info("Table truncated successfully")
        except Exception as e:
            # Table doesn't exist, create it
            logger.info(f"Table doesn't exist, creating {oracle_table_name}")
            create_table_sql = generate_create_table_sql(oracle_table_name, df)
            logger.info(f"Create table SQL: {create_table_sql}")
            oracle_cursor.execute(create_table_sql)
            oracle_conn.commit()
            logger.info("Table created successfully")

        # Dynamically build insert statement based on DataFrame columns
        placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
        insert_sql = f"INSERT INTO {oracle_table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        logger.info(f"Insert SQL: {insert_sql}")

        rows_inserted = 0
        batch = []

        for idx, row in df.iterrows():
            # Convert row to tuple, handling None values and type conversions
            row_values = []
            for col in columns:
                val = row[col]
                # Handle pandas NA/NaN values
                if val is None or (hasattr(val, '__class__') and 'NA' in val.__class__.__name__):
                    row_values.append(None)
                elif isinstance(val, bool):
                    row_values.append(1 if val else 0)
                else:
                    row_values.append(val)

            batch.append(tuple(row_values))

            if len(batch) >= batch_size:
                oracle_cursor.executemany(insert_sql, batch)
                oracle_conn.commit()
                rows_inserted += len(batch)
                logger.info(f"Inserted {rows_inserted} rows...")
                batch = []

        # Insert remaining rows
        if batch:
            oracle_cursor.executemany(insert_sql, batch)
            oracle_conn.commit()
            rows_inserted += len(batch)

        logger.info(f"Migration complete! Total rows inserted: {rows_inserted}")

        # Verify count
        oracle_cursor.execute(f"SELECT COUNT(*) FROM {oracle_table_name}")
        oracle_count = oracle_cursor.fetchone()[0]

        oracle_cursor.close()
        oracle_conn.close()

        result = {
            "status": "success",
            "rows_migrated": rows_inserted,
            "total_rows_in_oracle": oracle_count,
            "source": f"{share_name}.{schema_name}.{table_name}",
            "destination": oracle_table_name
        }

        logger.info(f"Result: {result}")

        return response.Response(
            ctx,
            response_data=json.dumps(result),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}", exc_info=True)
        return response.Response(
            ctx,
            response_data=json.dumps({
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }),
            headers={"Content-Type": "application/json"},
            status_code=500
        )


def generate_create_table_sql(table_name, df):
    """
    Generate CREATE TABLE SQL based on pandas DataFrame schema
    """
    import pandas as pd
    import numpy as np

    column_definitions = []
    for col in df.columns:
        dtype = df[col].dtype

        # Map pandas dtypes to Oracle types
        if pd.api.types.is_integer_dtype(dtype):
            oracle_type = "NUMBER"
        elif pd.api.types.is_float_dtype(dtype):
            oracle_type = "NUMBER"
        elif pd.api.types.is_bool_dtype(dtype):
            oracle_type = "NUMBER(1)"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            oracle_type = "DATE"
        else:
            # Default to VARCHAR2 for strings and unknown types
            oracle_type = "VARCHAR2(4000)"

        column_definitions.append(f"{col} {oracle_type}")

    create_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(column_definitions) + "\n)"
    return create_sql


def get_oracle_connection(user, password, dsn, wallet_location=None, wallet_password=None):
    """
    Connect to Oracle ATP database
    """
    if wallet_location:
        # For ATP with wallet
        return oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=wallet_password
        )
    else:
        # For regular connection or TLS without wallet
        return oracledb.connect(user=user, password=password, dsn=dsn)
