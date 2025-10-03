#!/usr/bin/env python3
"""
Configure the OCI Function with environment variables for database access
"""
import oci
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function details
FUNCTION_ID = "ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq"

def configure_function():
    """Add environment variables to the function configuration"""

    # Load OCI config
    config = oci.config.from_file()

    # Create Functions Management client
    functions_client = oci.functions.FunctionsManagementClient(config)

    # Configuration to add to the function
    function_config = {
        # Oracle ATP Configuration
        "ORACLE_USER": os.getenv("ORACLE_USER", "ADMIN"),
        "ORACLE_PASSWORD": os.getenv("ORACLE_PASSWORD", ""),
        "ORACLE_DSN": os.getenv("ORACLE_DSN", ""),

        # Note: Wallet needs to be included in Docker image or Object Storage
        # For now, we'll skip wallet and use mTLS if needed
    }

    print("Configuring function with environment variables:")
    for key in function_config.keys():
        # Don't print passwords
        if "PASSWORD" in key or "TOKEN" in key:
            print(f"  {key}: ********")
        else:
            print(f"  {key}: {function_config[key]}")

    try:
        # Update function configuration
        update_function_details = oci.functions.models.UpdateFunctionDetails(
            config=function_config
        )

        response = functions_client.update_function(
            function_id=FUNCTION_ID,
            update_function_details=update_function_details
        )

        print("\n✓ Function configuration updated successfully!")
        print(f"\nFunction Name: {response.data.display_name}")
        print(f"Function State: {response.data.lifecycle_state}")

    except oci.exceptions.ServiceError as e:
        print(f"\n✗ Error updating function: {e.message}")
        raise

if __name__ == "__main__":
    configure_function()
