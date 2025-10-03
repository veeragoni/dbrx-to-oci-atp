#!/bin/bash

# Automated GitHub Secrets Setup using GitHub CLI
# This script creates all required secrets for the GitHub Actions workflow

set -e

echo "=========================================="
echo "GitHub Secrets Setup (using gh CLI)"
echo "=========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo ""
    echo "Install it with:"
    echo "  macOS: brew install gh"
    echo "  Linux: See https://github.com/cli/cli#installation"
    echo ""
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ You are not authenticated with GitHub CLI"
    echo ""
    echo "Run: gh auth login"
    echo ""
    exit 1
fi

echo "✓ GitHub CLI is installed and authenticated"
echo ""

# Load environment variables
if [ ! -f infrastructure/.env ]; then
    echo "❌ infrastructure/.env not found"
    echo "Please create it from config/.env.example"
    exit 1
fi

source infrastructure/.env

# Get repository (current directory)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "$REPO" ]; then
    echo "❌ Not in a GitHub repository or repository not found"
    echo ""
    echo "Make sure you:"
    echo "1. Have pushed your code to GitHub"
    echo "2. Are in the repository directory"
    echo "3. Run: gh repo view"
    exit 1
fi

echo "📦 Repository: $REPO"
echo ""
echo "Creating secrets..."
echo ""

# 1. ORACLE_WALLET_BASE64
echo "1️⃣  Creating ORACLE_WALLET_BASE64..."
if [ -d "Wallet_NDG3D3LXZ4ESODQC" ]; then
    cd Wallet_NDG3D3LXZ4ESODQC
    zip -q -r ../wallet_temp.zip .
    cd ..
    WALLET_BASE64=$(base64 -i wallet_temp.zip)
    rm wallet_temp.zip
    echo "$WALLET_BASE64" | gh secret set ORACLE_WALLET_BASE64
    echo "   ✓ ORACLE_WALLET_BASE64 created"
else
    echo "   ⚠️  Wallet directory not found, skipping"
fi

# 2. OCIR_USERNAME
echo "2️⃣  Creating OCIR_USERNAME..."
OCIR_USERNAME="hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com"
echo "$OCIR_USERNAME" | gh secret set OCIR_USERNAME
echo "   ✓ OCIR_USERNAME created"

# 3. OCIR_TOKEN
echo "3️⃣  Creating OCIR_TOKEN..."
echo ""
echo "   ⚠️  You need to manually provide your OCI Auth Token"
echo "   Generate it at: OCI Console → Profile → User Settings → Auth Tokens"
echo ""
read -s -p "   Enter your OCI Auth Token: " OCIR_TOKEN
echo ""
if [ -n "$OCIR_TOKEN" ]; then
    echo "$OCIR_TOKEN" | gh secret set OCIR_TOKEN
    echo "   ✓ OCIR_TOKEN created"
else
    echo "   ⚠️  No token provided, skipping"
fi

# 4. OCI_USER_OCID
echo "4️⃣  Creating OCI_USER_OCID..."
if [ -n "$OCI_USER_OCID" ]; then
    echo "$OCI_USER_OCID" | gh secret set OCI_USER_OCID
    echo "   ✓ OCI_USER_OCID created"
else
    echo "   ⚠️  OCI_USER_OCID not found in .env"
fi

# 5. OCI_TENANCY_OCID
echo "5️⃣  Creating OCI_TENANCY_OCID..."
if [ -n "$OCI_TENANCY_OCID" ]; then
    echo "$OCI_TENANCY_OCID" | gh secret set OCI_TENANCY_OCID
    echo "   ✓ OCI_TENANCY_OCID created"
else
    echo "   ⚠️  OCI_TENANCY_OCID not found in .env"
fi

# 6. OCI_FINGERPRINT
echo "6️⃣  Creating OCI_FINGERPRINT..."
if [ -n "$OCI_FINGERPRINT" ]; then
    echo "$OCI_FINGERPRINT" | gh secret set OCI_FINGERPRINT
    echo "   ✓ OCI_FINGERPRINT created"
else
    echo "   ⚠️  OCI_FINGERPRINT not found in .env"
fi

# 7. OCI_PRIVATE_KEY
echo "7️⃣  Creating OCI_PRIVATE_KEY..."
if [ -f "$OCI_PRIVATE_KEY_PATH" ]; then
    cat "$OCI_PRIVATE_KEY_PATH" | gh secret set OCI_PRIVATE_KEY
    echo "   ✓ OCI_PRIVATE_KEY created"
else
    echo "   ⚠️  Private key file not found: $OCI_PRIVATE_KEY_PATH"
fi

echo ""
echo "=========================================="
echo "✅ GitHub Secrets Setup Complete!"
echo "=========================================="
echo ""
echo "Verify secrets:"
echo "  gh secret list"
echo ""
echo "Or view in browser:"
echo "  https://github.com/$REPO/settings/secrets/actions"
echo ""
echo "Test the workflow:"
echo "  git push origin main"
echo "  gh workflow view"
echo ""
