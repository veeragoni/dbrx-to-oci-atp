#!/bin/bash

# Add OCIR_TOKEN secret separately
# Use this after generating your OCI Auth Token

echo "Adding OCIR_TOKEN to GitHub Secrets..."
echo ""
echo "Generate your token at:"
echo "OCI Console → Profile → User Settings → Auth Tokens"
echo ""

read -s -p "Enter your OCI Auth Token: " OCIR_TOKEN
echo ""

if [ -z "$OCIR_TOKEN" ]; then
    echo "❌ No token provided"
    exit 1
fi

echo "$OCIR_TOKEN" | gh secret set OCIR_TOKEN

echo "✓ OCIR_TOKEN created successfully!"
echo ""
echo "Verify with: gh secret list"
