#!/bin/bash

# Create base64-encoded wallet for GitHub Secret
# This script creates a base64 string you can paste into GitHub Secrets

echo "Creating base64-encoded wallet for GitHub Secret..."
echo ""

cd Wallet_NDG3D3LXZ4ESODQC
zip -r ../wallet.zip .
cd ..

echo "Base64-encoded wallet (copy this to GitHub Secret 'ORACLE_WALLET_BASE64'):"
echo "=========================================================================="
base64 -i wallet.zip
echo "=========================================================================="
echo ""

rm wallet.zip

echo "To add this to GitHub:"
echo "1. Go to your GitHub repo → Settings → Secrets and variables → Actions"
echo "2. Click 'New repository secret'"
echo "3. Name: ORACLE_WALLET_BASE64"
echo "4. Value: Paste the base64 string above"
echo "5. Click 'Add secret'"
