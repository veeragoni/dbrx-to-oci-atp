#!/bin/bash

# Script to reorganize project structure
set -e

echo "Reorganizing project structure..."

# Create new directory structure
mkdir -p docs
mkdir -p scripts
mkdir -p tests
mkdir -p config

# Move documentation files
echo "Moving documentation..."
mv DEPLOYMENT.md docs/ 2>/dev/null || true
mv DEPLOYMENT_STEPS.md docs/ 2>/dev/null || true
mv OIC_INTEGRATION_GUIDE.md docs/ 2>/dev/null || true
mv BUILD_ON_X86.md docs/ 2>/dev/null || true
mv SECURITY_CHECKLIST.md docs/ 2>/dev/null || true

# Move configuration examples
echo "Moving configuration files..."
mv .env.example config/ 2>/dev/null || true
mv config.share.example config/ 2>/dev/null || true

# Move scripts
echo "Moving scripts..."
mv test_function.py scripts/ 2>/dev/null || true
mv test_simple.py scripts/ 2>/dev/null || true
mv check_function_ready.py scripts/ 2>/dev/null || true
mv check_logs.py scripts/ 2>/dev/null || true
mv configure_function.py scripts/ 2>/dev/null || true
mv list_delta_shares.py scripts/ 2>/dev/null || true
mv ocir-login.sh scripts/ 2>/dev/null || true
mv enable_logging.sh scripts/ 2>/dev/null || true
mv create_wallet_secret.sh scripts/ 2>/dev/null || true

# Move SQL files
echo "Moving SQL files..."
mv create_test_table.sql scripts/ 2>/dev/null || true

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

echo "✓ Reorganization complete!"
echo ""
echo "New structure:"
echo "  docs/          - All documentation"
echo "  scripts/       - Test and utility scripts"
echo "  config/        - Configuration examples"
echo "  function/      - OCI Function code"
echo "  infrastructure/ - CDKTF infrastructure code"
echo "  .github/       - GitHub Actions workflows"
