#!/bin/bash

# Test OCIR login locally before using in GitHub Actions

echo "Testing OCIR Login..."
echo ""

# Test credentials
OCIR_USERNAME="hpctraininglab/scegpu/suresh.veeragoni@oracle.com"
OCIR_REGISTRY="iad.ocir.io"

echo "Registry: $OCIR_REGISTRY"
echo "Username: $OCIR_USERNAME"
echo ""
echo "Enter your OCI Auth Token (the same one you added to GitHub):"
read -s OCIR_TOKEN
echo ""

echo "Attempting login..."
echo "$OCIR_TOKEN" | docker login "$OCIR_REGISTRY" -u "$OCIR_USERNAME" --password-stdin

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! OCIR login works!"
    echo ""
    echo "Now test pushing an image:"
    echo "  docker pull hello-world"
    echo "  docker tag hello-world $OCIR_REGISTRY/hpctraininglab/atp-repo:test"
    echo "  docker push $OCIR_REGISTRY/hpctraininglab/atp-repo:test"
    echo ""
    echo "If push succeeds, GitHub Actions will work too!"
else
    echo ""
    echo "❌ FAILED! Login unsuccessful."
    echo ""
    echo "Possible issues:"
    echo "1. Auth token is incorrect or expired"
    echo "2. Username format is wrong"
    echo "3. User doesn't have permissions to access this repository"
    echo ""
    echo "Verify:"
    echo "- Auth token is valid (not expired, not deleted)"
    echo "- Username is: $OCIR_USERNAME"
    echo "- User has access to repository: hpctraininglab/atp-repo"
    echo ""
    echo "Check repository policies in OCI Console:"
    echo "  Developer Services → Container Registry → atp-repo"
fi
