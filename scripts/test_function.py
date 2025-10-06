#!/usr/bin/env python3
"""
Test script to invoke the OCI Function locally
"""
import oci
import json

# Function details from deployment output
FUNCTION_ID = "ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq"
INVOKE_ENDPOINT = "https://f76itdjozpa.us-ashburn-1.functions.oci.oraclecloud.com"

def invoke_function(payload: dict = None):
    """
    Invoke the OCI Function with a payload

    Args:
        payload: Dictionary with function input data
    """
    # Load OCI config from default location (~/.oci/config)
    config = oci.config.from_file()

    # Create Functions Invoke client
    functions_client = oci.functions.FunctionsInvokeClient(
        config=config,
        service_endpoint=INVOKE_ENDPOINT
    )

    # Default payload if none provided
    if payload is None:
        # Read and encode the delta share profile
        import base64
        import os
        from dotenv import load_dotenv

        load_dotenv()

        # Read delta share profile (from project root)
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        share_path = os.path.join(project_root, 'demo.share')

        with open(share_path, 'r') as f:
            profile_content = f.read()

        profile_b64 = base64.b64encode(profile_content.encode()).decode()

        payload = {
            "delta_profile_base64": profile_b64,
            "share_name": "delta_sharing",  # From list_delta_shares.py output
            "schema_name": "default",
            "table_name": "boston-housing",  # Boston housing dataset
            "oracle_user": os.getenv("ORACLE_USER", "ADMIN"),
            "oracle_password": os.getenv("ORACLE_PASSWORD"),
            "oracle_dsn": os.getenv("ORACLE_DSN"),
            "oracle_wallet_location": "/function/wallet",  # Wallet location in Docker container
            "oracle_wallet_password": os.getenv("ORACLE_WALLET_PASSWORD"),
            "batch_size": 100,
            "limit_rows": 10,  # Limit to 10 rows for testing
            "oracle_table_name": "BOSTON_HOUSING"  # Target table in ATP
        }

    print(f"Invoking function with payload:")
    print(json.dumps(payload, indent=2))
    print()

    try:
        # Invoke the function
        response = functions_client.invoke_function(
            function_id=FUNCTION_ID,
            invoke_function_body=json.dumps(payload),
            fn_intent="httprequest",
            fn_invoke_type="sync"  # Synchronous invocation
        )

        # Read and decode response
        response_data = response.data.text if hasattr(response.data, 'text') else response.data

        print("Function Response:")
        print("=" * 80)
        print(response_data)
        print("=" * 80)

        # Try to parse as JSON
        try:
            result = json.loads(response_data)
            print("\nParsed JSON Response:")
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError:
            print("\nResponse is not JSON format")

        return response_data

    except oci.exceptions.ServiceError as e:
        print(f"Service Error: {e.message}")
        print(f"Status: {e.status}")
        print(f"Code: {e.code}")
        raise
    except Exception as e:
        print(f"Error invoking function: {str(e)}")
        raise


if __name__ == "__main__":
    import sys

    # You can pass a custom payload as JSON string argument
    if len(sys.argv) > 1:
        try:
            payload = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print("Invalid JSON payload provided")
            sys.exit(1)
    else:
        payload = None

    invoke_function(payload)
