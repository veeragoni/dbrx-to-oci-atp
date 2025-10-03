#!/bin/bash

# Simple OCIR Login Helper
# This script helps you login to Oracle Container Image Registry

echo "=== OCIR Login Helper ==="
echo ""
echo "You need the following information:"
echo "1. Tenancy Namespace (shown in your OCI Console under Tenancy details)"
echo "2. Your OCI Username"
echo "3. An Auth Token (NOT your regular password)"
echo ""
echo "If you don't have an Auth Token:"
echo "  1. Go to OCI Console"
echo "  2. Click your profile icon (top right) -> User Settings"
echo "  3. Click 'Auth Tokens' on the left"
echo "  4. Click 'Generate Token'"
echo "  5. Copy the token (you can't see it again!)"
echo ""

read -p "Enter your tenancy namespace: " TENANCY_NAMESPACE
read -p "Enter your OCI username: " OCI_USERNAME
echo -n "Enter your auth token (input will be hidden): "
read -s AUTH_TOKEN
echo ""

# Construct the full username
FULL_USERNAME="${TENANCY_NAMESPACE}/${OCI_USERNAME}"

# Extract region from OCIR_REPOSITORY if it exists in .env
if [ -f .env ]; then
    source .env
    if [ ! -z "$OCIR_REPOSITORY" ]; then
        REGION=$(echo $OCIR_REPOSITORY | cut -d'.' -f1)
        REGISTRY="${REGION}.ocir.io"
    fi
fi

# If we couldn't extract, ask user
if [ -z "$REGISTRY" ]; then
    echo ""
    echo "Common regions: iad (Ashburn), phx (Phoenix), fra (Frankfurt)"
    read -p "Enter your region code (e.g., iad, phx): " REGION_CODE
    REGISTRY="${REGION_CODE}.ocir.io"
fi

echo ""
echo "Logging in to ${REGISTRY}..."
echo "Username: ${FULL_USERNAME}"

echo "${AUTH_TOKEN}" | docker login ${REGISTRY} -u "${FULL_USERNAME}" --password-stdin

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully logged in to OCIR!"
    echo ""
    echo "You can now run: ./infrastructure/deploy.sh"
else
    echo ""
    echo "✗ Login failed. Please check your credentials and try again."
fi
