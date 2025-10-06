#!/bin/bash

# Helper script to display values needed for GitHub Secrets
# DO NOT commit the output of this script!

echo "=============================================="
echo "GitHub Secrets Values"
echo "=============================================="
echo ""
echo "⚠️  WARNING: These are SECRETS - Do not share!"
echo ""

echo "1. ORACLE_WALLET_BASE64"
echo "   Run: ./scripts/create_wallet_secret.sh"
echo ""

echo "2. OCIR_USERNAME"
echo "   Value: hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com"
echo ""

echo "3. OCIR_TOKEN"
echo "   Go to: OCI Console → Profile → User Settings → Auth Tokens"
echo "   Click 'Generate Token' and copy the value"
echo ""

if [ -f infrastructure/.env ]; then
    source infrastructure/.env

    echo "4. OCI_USER_OCID"
    echo "   Value: ${OCI_USER_OCID}"
    echo ""

    echo "5. OCI_TENANCY_OCID"
    echo "   Value: ${OCI_TENANCY_OCID}"
    echo ""

    echo "6. OCI_FINGERPRINT"
    echo "   Value: ${OCI_FINGERPRINT}"
    echo ""

    echo "7. OCI_PRIVATE_KEY"
    if [ -f "${OCI_PRIVATE_KEY_PATH}" ]; then
        echo "   Content of: ${OCI_PRIVATE_KEY_PATH}"
        echo "   (Include entire content with BEGIN/END lines)"
        echo ""
        echo "   Preview (first 2 lines):"
        head -2 "${OCI_PRIVATE_KEY_PATH}"
        echo "   ..."
    else
        echo "   File not found: ${OCI_PRIVATE_KEY_PATH}"
    fi
else
    echo "ERROR: infrastructure/.env not found"
    echo "Please create it from config/.env.example"
fi

echo ""
echo "=============================================="
echo "Add these at:"
echo "https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "=============================================="
