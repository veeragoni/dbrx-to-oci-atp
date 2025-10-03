#!/usr/bin/env python3
"""
Check if OCI Function is ready to be invoked
"""
import oci
import time
from datetime import datetime, timedelta

FUNCTION_ID = "ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq"

def check_function_status():
    config = oci.config.from_file()
    functions_client = oci.functions.FunctionsManagementClient(config)

    response = functions_client.get_function(function_id=FUNCTION_ID)
    func = response.data

    print("Function Status:")
    print(f"  Name: {func.display_name}")
    print(f"  State: {func.lifecycle_state}")
    print(f"  Image: {func.image}")
    print(f"  Image Digest: {func.image_digest}")
    print(f"  Last Updated: {func.time_updated}")
    print(f"  Memory: {func.memory_in_mbs}MB")
    print(f"  Timeout: {func.timeout_in_seconds}s")
    print()

    # Check how recent the update was
    updated_time = func.time_updated
    now = datetime.now(updated_time.tzinfo)
    time_since_update = now - updated_time

    print(f"Time since last update: {time_since_update.total_seconds():.0f} seconds")

    if func.lifecycle_state == "ACTIVE":
        print("✓ Function is ACTIVE")

        if time_since_update < timedelta(seconds=30):
            print("⚠ Function was just updated. Wait 30-60 seconds before invoking.")
            print(f"  Recommended wait: {max(0, 60 - int(time_since_update.total_seconds()))} more seconds")
            return False
        else:
            print("✓ Function should be ready to invoke")
            return True
    else:
        print(f"✗ Function is not ACTIVE (state: {func.lifecycle_state})")
        return False

if __name__ == "__main__":
    ready = check_function_status()

    if ready:
        print("\n➜ You can now test the function:")
        print("   python test_simple.py")
    else:
        print("\n⏳ Wait a bit longer before testing")
