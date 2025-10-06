# DBRX to ATP Migration - OCI Function Deployment Guide

This guide provides complete instructions for deploying the Databricks to Oracle ATP migration function using CDKTF (Cloud Development Kit for Terraform) and invoking it from Oracle Integration Cloud (OIC).

## Architecture Overview

The solution consists of:
1. **OCI Function**: Python function that reads data from Databricks Delta Share and migrates to Oracle ATP
2. **CDKTF Infrastructure**: TypeScript-based infrastructure as code using Terraform CDK
3. **OIC Integration**: Oracle Integration Cloud can invoke the function directly

## Prerequisites

### Required Tools
- Node.js >= 18.0
- npm or yarn
- Terraform >= 1.5
- CDKTF CLI >= 0.20
- Docker
- OCI CLI (fn CLI) - [Installation Guide](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinstallfncli.htm)

### Install CDKTF CLI
```bash
npm install -g cdktf-cli@latest
```

### Install Fn CLI
```bash
# macOS
brew install fn

# Linux
curl -LSs https://raw.githubusercontent.com/fnproject/cli/master/install | sh
```

### OCI Requirements
- OCI Account with necessary permissions
- OCI API Key configured
- Compartment OCID
- VCN and Subnet (or will be created by CDKTF)
- Oracle Container Registry (OCIR) access
- Auth Token for OCIR push

## Step 1: Configuration

### 1.1 Configure OCI CLI
```bash
oci setup config
```

### 1.2 Setup Environment Variables
```bash
cd infrastructure
cp .env.example .env
```

Edit `.env` with your values:
```bash
# OCI Authentication
OCI_TENANCY_OCID=ocid1.tenancy.oc1..aaaa...
OCI_USER_OCID=ocid1.user.oc1..aaaa...
OCI_FINGERPRINT=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
OCI_PRIVATE_KEY_PATH=~/.oci/oci_api_key.pem
OCI_REGION=us-phoenix-1
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..aaaa...

# OCIR Repository
# Format: <region-key>.ocir.io/<namespace>/<repository-name>
OCIR_REPOSITORY=phx.ocir.io/mytenancy/dbrx-to-atp
```

### 1.3 Login to OCIR
```bash
# Get your namespace
oci os ns get

# Login to Docker
docker login <region>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>
```

To create an auth token:
1. Go to OCI Console → User Settings → Auth Tokens
2. Click "Generate Token"
3. Save the token (you won't see it again)

## Step 2: Deploy Infrastructure

### Option A: Automated Deployment
```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual Deployment

#### 2.1 Install Dependencies
```bash
cd infrastructure
npm install
```

#### 2.2 Get Terraform Providers
```bash
cdktf get
```

#### 2.3 Build Function Image
```bash
cd ../function

# Build function
fn build --verbose

# Tag image
docker tag dbrx-to-atp-migration:0.0.1 ${OCIR_REPOSITORY}:latest

# Push to OCIR
docker push ${OCIR_REPOSITORY}:latest
```

#### 2.4 Deploy CDKTF Stack
```bash
cd ../infrastructure

# Synthesize Terraform configuration
cdktf synth

# Deploy
cdktf deploy
```

## Step 3: Verify Deployment

After deployment, CDKTF will output:
```
Outputs:
  function-id = ocid1.fnfunc.oc1.phx.aaaa...
  function-invoke-endpoint = https://...
  application-id = ocid1.fnapp.oc1.phx.aaaa...
  oic-integration-info = {"compartmentId":"...","functionId":"...","invokeEndpoint":"...","region":"..."}
```

### Test the Function
```bash
# Using OCI CLI
echo '{
  "delta_profile_base64": "<base64-encoded-delta-share-profile>",
  "share_name": "delta_sharing",
  "schema_name": "default",
  "table_name": "boston-housing",
  "oracle_user": "ADMIN",
  "oracle_password": "YourPassword",
  "oracle_dsn": "yourdb_high",
  "oracle_wallet_location": "/tmp/wallet",
  "batch_size": 100,
  "limit_rows": 200,
  "oracle_table_name": "boston_housing"
}' | fn invoke dbrx-to-atp-app dbrx-to-atp-migration
```

## Step 4: Configure OIC Integration

### 4.1 Create Dynamic Group (if not exists)
In OCI Console → Identity → Dynamic Groups, create:

Name: `dbrx-to-atp-fn-dg`

Matching Rules:
```
ALL {resource.type = 'fnfunc', resource.compartment.id = '<your-compartment-ocid>'}
```

### 4.2 OIC Function Invocation Setup

1. **Open OIC Console**
   - Navigate to your Oracle Integration Cloud instance

2. **Create Integration**
   - Click "Integrations" → "Create"
   - Select "App Driven Orchestration"
   - Name: "DBRX to ATP Migration"

3. **Add REST Trigger** (Optional - for external invocation)
   - Configure REST endpoint
   - Define request payload schema

4. **Add OCI Function Action**
   - Drag "Oracle Cloud Infrastructure" from palette
   - Select "Invoke Function"
   - Configure:
     - **Region**: Select your OCI region (e.g., us-phoenix-1)
     - **Compartment**: Select the compartment containing the function
     - **Function Application**: Select "dbrx-to-atp-app"
     - **Function**: Select "dbrx-to-atp-migration"

5. **Configure Request Mapping**
   Map input parameters to function payload:
   ```json
   {
     "delta_profile_base64": "<from-trigger-or-variable>",
     "share_name": "delta_sharing",
     "schema_name": "default",
     "table_name": "boston-housing",
     "oracle_user": "ADMIN",
     "oracle_password": "YourPassword",
     "oracle_dsn": "yourdb_high",
     "oracle_wallet_location": "/tmp/wallet",
     "oracle_wallet_password": null,
     "batch_size": 100,
     "limit_rows": 200,
     "oracle_table_name": "boston_housing"
   }
   ```

   **Security Best Practice**: Use OCI Vault to store credentials and reference them instead of hardcoding.

6. **Configure Response Mapping**
   Map function response to integration outputs:
   ```json
   {
     "status": "success",
     "rows_migrated": 200,
     "total_rows_in_oracle": 200,
     "source": "delta_sharing.default.boston-housing",
     "destination": "boston_housing"
   }
   ```

7. **Activate Integration**
   - Click "Activate"
   - Enable tracing for debugging

### 4.3 Test from OIC
1. Click "Run" in the integration
2. Provide test input
3. Monitor execution in Activity Stream

## Function Input Schema

```json
{
  "delta_profile_base64": "base64-encoded Delta Share profile content",
  "share_name": "name of the Delta Share",
  "schema_name": "schema name in Delta Share",
  "table_name": "table name to read",
  "oracle_user": "Oracle username (e.g., ADMIN)",
  "oracle_password": "Oracle password",
  "oracle_dsn": "Oracle connection string (e.g., yourdb_high)",
  "oracle_wallet_location": "Path to wallet directory (optional, e.g., /tmp/wallet)",
  "oracle_wallet_password": "Wallet password (optional, usually null)",
  "batch_size": 100,
  "limit_rows": null,
  "oracle_table_name": "target_table_name"
}
```

### Encoding Delta Share Profile
```bash
base64 -i your-profile.share
```

Or in Python:
```python
import base64
with open('your-profile.share', 'r') as f:
    encoded = base64.b64encode(f.read().encode()).decode()
    print(encoded)
```

## Function Output Schema

Success:
```json
{
  "status": "success",
  "rows_migrated": 200,
  "total_rows_in_oracle": 200,
  "source": "delta_sharing.default.boston-housing",
  "destination": "boston_housing"
}
```

Error:
```json
{
  "status": "error",
  "error": "Error message",
  "type": "ExceptionType"
}
```

## Managing Secrets (Production)

For production deployments, use OCI Vault instead of passing credentials directly:

### 1. Create Vault and Secrets
```bash
# Create vault (one-time)
oci kms management vault create --compartment-id <compartment-ocid> --display-name dbrx-to-atp-vault --vault-type DEFAULT

# Create secrets
oci vault secret create-base64 \
  --compartment-id <compartment-ocid> \
  --secret-name oracle-atp-password \
  --vault-id <vault-ocid> \
  --key-id <key-ocid> \
  --secret-content-content <base64-encoded-password>
```

### 2. Update Function to Read from Vault
Modify [func.py](../function/func.py) to retrieve secrets using OCI SDK.

### 3. Update IAM Policies
```
Allow dynamic-group dbrx-to-atp-fn-dg to read secret-family in compartment id <compartment-ocid>
```

## Monitoring and Troubleshooting

### View Function Logs
```bash
# Via OCI CLI
fn logs get <app-name> <function-name>

# Via OCI Console
Navigate to Functions → Application → Function → Logs
```

### Common Issues

**Issue**: Function timeout
- **Solution**: Increase timeout in [func.yaml](../function/func.yaml) or infrastructure/main.ts (max 300s)

**Issue**: Out of memory
- **Solution**: Increase memory in [func.yaml](../function/func.yaml) or infrastructure/main.ts (up to 2048 MB)

**Issue**: Cannot connect to ATP
- **Solution**:
  - Verify wallet is accessible
  - Check network connectivity
  - Verify credentials

**Issue**: Docker push fails
- **Solution**:
  - Verify OCIR login: `docker login <region>.ocir.io`
  - Check auth token is valid
  - Verify repository name format

## Cleanup

To destroy all resources:
```bash
cd infrastructure
cdktf destroy
```

## Additional Resources

- [OCI Functions Documentation](https://docs.oracle.com/en-us/iaas/Content/Functions/home.htm)
- [OIC Functions Integration](https://docs.oracle.com/en/cloud/paas/application-integration/integrations-user/invoke-oracle-cloud-infrastructure-functions-directly-integration-oci-function-action.html)
- [CDKTF Documentation](https://developer.hashicorp.com/terraform/cdktf)
- [Delta Sharing Documentation](https://delta.io/sharing/)
- [Oracle ATP Documentation](https://docs.oracle.com/en/cloud/paas/atp-cloud/)

## Support and Contributing

For issues or questions, please create an issue in the repository.
