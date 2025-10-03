#!/usr/bin/env python3
"""
Simple test to check if function starts and returns any response
"""
import oci
import json

FUNCTION_ID = "ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq"
INVOKE_ENDPOINT = "https://f76itdjozpa.us-ashburn-1.functions.oci.oraclecloud.com"

config = oci.config.from_file()
functions_client = oci.functions.FunctionsInvokeClient(
    config=config,
    service_endpoint=INVOKE_ENDPOINT
)

# Send minimal payload to test if function responds
minimal_payload = {}

print("Testing function with empty payload...")
try:
    response = functions_client.invoke_function(
        function_id=FUNCTION_ID,
        invoke_function_body=json.dumps(minimal_payload),
        fn_intent="httprequest",
        fn_invoke_type="sync"
    )

    print("Response received!")
    print("Status:", response.status)
    print("Headers:", response.headers)
    print("Data:", response.data)

except Exception as e:
    print(f"Error: {e}")
    print(f"\nError type: {type(e).__name__}")
    if hasattr(e, 'status'):
        print(f"Status: {e.status}")
    if hasattr(e, 'code'):
        print(f"Code: {e.code}")
