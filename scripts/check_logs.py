#!/usr/bin/env python3
"""
Check OCI Function logs to debug execution issues
"""
import oci
from datetime import datetime, timedelta

# Function details
FUNCTION_ID = "ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq"
APPLICATION_ID = "ocid1.fnapp.oc1.iad.amaaaaaa52tswuaagpecmdqlsbluyur2rvrr33yeftzoggenff76itdjozpa"
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaa6nehdn756cywayo4ybjgr5nutln4ygcvws6j2yookyvjfdamzera"

def get_function_logs():
    """Fetch recent function logs"""

    config = oci.config.from_file()

    # Create Logging Search client
    logging_search_client = oci.loggingsearch.LogSearchClient(config)

    # Search for logs from the last 30 minutes
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)

    search_query = f"""
    search "{COMPARTMENT_ID}"
    | where type='com.oraclecloud.functions.invoke'
    | sort by datetime desc
    """

    print(f"Searching for function logs from {start_time} to {end_time}...")
    print()

    try:
        search_logs_details = oci.loggingsearch.models.SearchLogsDetails(
            time_start=start_time,
            time_end=end_time,
            search_query=search_query,
            is_return_field_info=False
        )

        response = logging_search_client.search_logs(
            search_logs_details=search_logs_details
        )

        if response.data.results:
            print(f"Found {len(response.data.results)} log entries:")
            print("=" * 100)

            for i, log in enumerate(response.data.results, 1):
                print(f"\n[{i}] Time: {log.data.get('datetime', 'N/A')}")
                print(f"Type: {log.data.get('type', 'N/A')}")
                print(f"Message: {log.data.get('message', 'N/A')}")

                # Print full log data
                print("\nFull log data:")
                for key, value in log.data.items():
                    print(f"  {key}: {value}")
                print("-" * 100)
        else:
            print("No logs found. This could mean:")
            print("1. Logging is not configured for the function")
            print("2. The function hasn't been invoked recently")
            print("3. Logs haven't been indexed yet (wait a minute and try again)")

    except Exception as e:
        print(f"Error fetching logs: {str(e)}")
        print("\nAlternative: Check logs in OCI Console:")
        print(f"1. Go to: Functions → Applications → dbrx-to-atp-app")
        print(f"2. Click on 'Logs' tab")
        print(f"3. Or go to: Logging → Log Search")

if __name__ == "__main__":
    get_function_logs()
