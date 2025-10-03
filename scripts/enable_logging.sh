#!/bin/bash

# Enable logging for OCI Functions Application
# This will help us debug the 502 errors

APPLICATION_ID="ocid1.fnapp.oc1.iad.amaaaaaa52tswuaagpecmdqlsbluyur2rvrr33yeftzoggenff76itdjozpa"
COMPARTMENT_ID="ocid1.compartment.oc1..aaaaaaaa6nehdn756cywayo4ybjgr5nutln4ygcvws6j2yookyvjfdamzera"

echo "To enable function logging, you need to:"
echo ""
echo "1. Go to OCI Console:"
echo "   https://cloud.oracle.com/functions/applications/${APPLICATION_ID}"
echo ""
echo "2. Click 'Logs' tab"
echo ""
echo "3. Click 'Enable Log'"
echo ""
echo "4. Or create a log group and log via CLI:"
echo ""
echo "# Create log group"
echo "oci logging log-group create \\"
echo "  --compartment-id ${COMPARTMENT_ID} \\"
echo "  --display-name \"functions-log-group\""
echo ""
echo "# Then enable invoke logs for the application"
echo "oci logging log create \\"
echo "  --log-group-id <log-group-ocid> \\"
echo "  --display-name \"dbrx-function-invoke-logs\" \\"
echo "  --log-type SERVICE \\"
echo "  --configuration '{\"source\":{\"service\":\"functions\",\"resource\":\"'${APPLICATION_ID}'\",\"category\":\"invoke\",\"sourceType\":\"OCISERVICE\"},\"archiving\":{\"isEnabled\":false}}'"
echo ""
echo "After enabling logs, wait 1-2 minutes, then invoke the function and check logs."
