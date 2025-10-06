#!/bin/bash

# Deploy script for DBRX to ATP Migration Function
set -e

echo "=== DBRX to ATP Function Deployment ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=(
    "OCI_TENANCY_OCID"
    "OCI_USER_OCID"
    "OCI_FINGERPRINT"
    "OCI_PRIVATE_KEY_PATH"
    "OCI_REGION"
    "OCI_COMPARTMENT_ID"
    "OCIR_REPOSITORY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Error: $var is not set in .env${NC}"
        exit 1
    fi
done

echo -e "${BLUE}Step 1: Installing CDKTF dependencies...${NC}"
npm install

echo -e "${BLUE}Step 2: Getting Terraform providers...${NC}"
cdktf get

echo -e "${BLUE}Step 3: Building function Docker image...${NC}"
# Navigate to function directory
cd ../function

# Build and push Docker image using fn CLI
# Make sure you're logged into OCIR first:
# docker login <region>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>

echo "Building function for x86_64 platform (OCI Functions requirement)..."
# Build for linux/amd64 platform (x86_64) for OCI Functions compatibility
# Using docker build with platform flag to cross-compile from ARM Mac to x86_64
cd ../function
docker build --platform linux/amd64 -t dbrx-to-atp-migration:0.0.1 .
cd ../infrastructure

echo -e "${BLUE}Step 4: Checking if image needs to be pushed to OCIR...${NC}"

# Get local image digest
LOCAL_DIGEST=$(docker inspect --format='{{.Id}}' dbrx-to-atp-migration:0.0.1 2>/dev/null || echo "")

# Try to get remote image digest
REMOTE_DIGEST=$(docker manifest inspect ${OCIR_REPOSITORY}:latest 2>/dev/null | grep -oE '"digest":\s*"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")

if [ -n "$LOCAL_DIGEST" ] && [ -n "$REMOTE_DIGEST" ]; then
    echo "Local image digest: ${LOCAL_DIGEST}"
    echo "Remote image digest: ${REMOTE_DIGEST}"

    # Note: digests might be different even for same content due to metadata
    # So we'll just inform the user and ask
    echo -e "${BLUE}Image already exists in OCIR. Do you want to push again? (y/n)${NC}"
    read -r PUSH_CHOICE
    if [[ ! "$PUSH_CHOICE" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Skipping push - using existing image${NC}"
        SKIP_PUSH=true
    fi
fi

if [ "$SKIP_PUSH" != "true" ]; then
    # Tag the image
    docker tag dbrx-to-atp-migration:0.0.1 ${OCIR_REPOSITORY}:latest

    # Push to OCIR
    docker push ${OCIR_REPOSITORY}:latest

    echo -e "${GREEN}Function image pushed to ${OCIR_REPOSITORY}:latest${NC}"
else
    echo -e "${GREEN}Using existing image in OCIR${NC}"
fi

# Return to infrastructure directory
cd ../infrastructure

echo -e "${BLUE}Step 5: Synthesizing CDKTF stack...${NC}"
cdktf synth

echo -e "${BLUE}Step 6: Deploying infrastructure...${NC}"
cdktf deploy --auto-approve

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "To invoke the function from OIC, use the outputs above."
echo "Remember to configure OIC with the function OCID and invoke endpoint."
