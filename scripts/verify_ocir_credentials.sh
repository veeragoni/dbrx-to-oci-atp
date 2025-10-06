#!/bin/bash

# Script to help verify OCIR credentials

echo "=========================================="
echo "OCIR Credentials Verification Helper"
echo "=========================================="
echo ""

# Check tenancy namespace
echo "1️⃣  Verifying Tenancy Namespace..."
echo ""
echo "   Run this OCI CLI command to get your tenancy namespace:"
echo "   oci os ns get"
echo ""
oci os ns get 2>/dev/null && echo "" || echo "   (OCI CLI command failed - check manually in console)"

echo ""
echo "2️⃣  Check your username format..."
echo ""
echo "   For federated users (Oracle SSO), the format is usually:"
echo "   <tenancy-namespace>/<identity-provider>/<username>"
echo ""
echo "   Common identity providers:"
echo "   - oracleidentitycloudservice (default IDCS)"
echo "   - scegpu (custom identity provider)"
echo "   - oam (Oracle Access Manager)"
echo ""
echo "   Your current username: hpctraininglab/scegpu/suresh.veeragoni@oracle.com"
echo ""
echo "   To verify in OCI Console:"
echo "   1. Go to Identity → Federation"
echo "   2. Find your identity provider name"
echo "   3. Check Users tab"
echo ""

echo "3️⃣  Verify Auth Token..."
echo ""
echo "   Your auth tokens are at:"
echo "   OCI Console → Profile → User Settings → Auth Tokens"
echo ""
echo "   Make sure:"
echo "   - Token is not expired"
echo "   - Token is for the correct user (suresh.veeragoni@oracle.com)"
echo "   - Copy the EXACT token (no spaces, complete string)"
echo ""

echo "4️⃣  Test different username formats..."
echo ""
echo "   Try logging in with these formats:"
echo ""

# Try format 1
echo "   Format 1: hpctraininglab/scegpu/suresh.veeragoni@oracle.com"
echo "   docker login iad.ocir.io -u 'hpctraininglab/scegpu/suresh.veeragoni@oracle.com'"
echo ""

# Try format 2
echo "   Format 2: hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com"
echo "   docker login iad.ocir.io -u 'hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com'"
echo ""

# Try format 3
echo "   Format 3: hpctraininglab/suresh.veeragoni@oracle.com (if not federated)"
echo "   docker login iad.ocir.io -u 'hpctraininglab/suresh.veeragoni@oracle.com'"
echo ""

echo "5️⃣  Get repository details..."
echo ""
echo "   Check if repository exists and get its compartment:"
oci artifacts container repository list \
    --compartment-id ocid1.compartment.oc1..aaaaaaaa6nehdn756cywayo4ybjgr5nutln4ygcvws6j2yookyvjfdamzera \
    --display-name atp-repo \
    --query 'data.items[0].{"name":"display-name","compartment":"compartment-id","public":"is-public"}' 2>/dev/null && echo "" || echo "   (Could not retrieve repository info)"

echo ""
echo "=========================================="
echo "Manual Test:"
echo "=========================================="
echo ""
echo "Try this command with your auth token:"
echo ""
echo 'echo "YOUR_AUTH_TOKEN" | docker login iad.ocir.io -u "hpctraininglab/scegpu/suresh.veeragoni@oracle.com" --password-stdin'
echo ""
echo "If it fails, try the other username formats above."
echo ""
