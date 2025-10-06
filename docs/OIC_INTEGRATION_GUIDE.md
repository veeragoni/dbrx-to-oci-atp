# OIC Integration Guide - DBRX to ATP Function

This guide shows how to invoke the deployed OCI Function from Oracle Integration Cloud (OIC), based on the OIC Functions feature demonstration.

## Overview

Oracle Integration Cloud (OIC) provides native support for invoking OCI Functions directly from integrations. This allows you to create serverless data migration workflows that can be triggered from various sources.

### Invocation Options

OIC supports multiple ways to trigger your OCI Function:

**1. Manual/On-Demand Trigger:**
- ✅ **REST Adapter** - Invoke the function via HTTP request
- Trigger manually from OIC console
- Expose as a REST endpoint for external systems

**2. Scheduled Trigger:**
- ✅ **Schedule-based Integration** - Run automatically on a schedule (hourly, daily, weekly, etc.)
- Perfect for periodic data sync from Delta Share to ATP
- No manual intervention needed

**3. Event-Driven Trigger:**
- ✅ **OCI Events** - Trigger when specific OCI events occur
- ✅ **File/Object Storage** - Trigger when files are uploaded
- ✅ **Database Events** - Trigger on database changes

### Recommended Approach for DBRX to ATP Migration

**For Regular Data Sync (Most Common):**
```
OIC Schedule → OIC Integration → Invoke OCI Function → Data migrated to ATP
```
- Runs automatically (e.g., every hour, daily at midnight)
- Consistent, predictable data refresh
- Zero manual intervention

**For On-Demand Migration:**
```
User/System → REST API → OIC Integration → Invoke OCI Function → Data migrated
```
- Full control over when migration runs
- Useful for testing or irregular updates
- Can be triggered from external systems

## Prerequisites

1. Deployed OCI Function (see [DEPLOYMENT.md](DEPLOYMENT.md))
2. OIC instance in the same tenancy
3. Function OCID and invoke endpoint (from CDKTF outputs)
4. Appropriate IAM policies (see [Authentication](#authentication-methods) section below)

## Authentication Methods

OIC can authenticate to your OCI Function using two methods:

### Method 1: Resource Principal (Recommended)

The OIC instance is granted permission to invoke functions without explicit credentials.

**Required IAM Policy:**
```
Allow any-user to use fn-function in compartment <compartment-name>
  where ALL {
    request.principal.type='integration',
    request.principal.id='<oic-instance-ocid>'
  }
```

**Benefits:**
- ✅ No credentials to manage
- ✅ More secure (no API keys)
- ✅ Automatic credential rotation
- ✅ Easier to set up

### Method 2: OCI Signature Authentication

Configure OIC connection with OCI API key credentials.

**Required Setup:**
1. Generate API signing key pair
2. Add public key to OCI user
3. Configure OIC connection with:
   - Tenancy OCID
   - User OCID
   - Private Key
   - Fingerprint
   - Region

**When to Use:**
- Cross-tenancy function calls
- Need specific user attribution
- Advanced auditing requirements

## Step-by-Step Integration

### Step 1: Create OIC Integration

1. **Login to OIC Console**
   - Navigate to your OIC instance URL
   - Click "Integrations" from the left menu

2. **Create New Integration**
   - Click "Create"
   - Select "App Driven Orchestration"
   - Name: `DBRX_to_ATP_Migration`
   - Description: `Migrate data from Databricks to Oracle ATP using OCI Function`
   - Click "Create"

### Step 2: Add REST Trigger (For REST API Invocation)

**Use this step if you want to trigger the function via REST API.**

1. **Add REST Adapter**
   - Click on "+" in the integration canvas
   - Search for "REST" adapter
   - Configure:
     - **Name**: `TriggerMigration`
     - **Role**: Trigger
     - **Endpoint**: `/dbrx-to-atp`
     - **Action**: POST
     - **Request Format**: JSON
     - **Response Format**: JSON

2. **Define Request Payload Schema**

   Click "Request" tab and provide this **simplified** JSON schema:

   ```json
   {
     "share_name": "delta_sharing",
     "schema_name": "default",
     "table_name": "boston-housing",
     "oracle_table_name": "boston_housing",
     "batch_size": 100,
     "limit_rows": 200
   }
   ```

   **What Each Parameter Does:**

   | Parameter | Required? | Default | Description |
   |-----------|-----------|---------|-------------|
   | `share_name` | ✅ Yes | - | Delta Share name from profile.json |
   | `schema_name` | ✅ Yes | - | Schema name in Delta Share |
   | `table_name` | ✅ Yes | - | Table name in Delta Share |
   | `oracle_table_name` | ❌ No | Same as `table_name` | Target table name in ATP |
   | `batch_size` | ❌ No | `100` | Rows per batch for insertion |
   | `limit_rows` | ❌ No | `null` (all) | Limit total rows (for testing) |

   **What You DON'T Need to Pass:**
   - ❌ `delta_profile_base64` - Embedded in Docker image
   - ❌ `oracle_user` - Function config variable
   - ❌ `oracle_password` - Function config variable
   - ❌ `oracle_dsn` - Function config variable
   - ❌ `oracle_wallet_location` - Embedded in Docker image
   - ❌ `oracle_wallet_password` - Not needed

3. **Example REST API Call from External System:**

   **Minimal Request (only required fields):**
   ```bash
   curl -X POST https://your-oic-instance/ic/api/integration/v1/flows/rest/DBRX_TO_ATP_MIGRATION/1.0/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic <base64-credentials>" \
     -d '{
       "share_name": "delta_sharing",
       "schema_name": "default",
       "table_name": "boston-housing"
     }'
   ```

   **Full Request (with optional parameters):**
   ```bash
   curl -X POST https://your-oic-instance/ic/api/integration/v1/flows/rest/DBRX_TO_ATP_MIGRATION/1.0/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic <base64-credentials>" \
     -d '{
       "share_name": "delta_sharing",
       "schema_name": "default",
       "table_name": "boston-housing",
       "oracle_table_name": "boston_housing_copy",
       "batch_size": 200,
       "limit_rows": 1000
     }'
   ```

   **Expected Response:**
   ```json
   {
     "status": "success",
     "rows_migrated": 506,
     "total_rows_in_oracle": 506,
     "source": "delta_sharing.default.boston-housing",
     "destination": "ADMIN.boston_housing"
   }
   ```

### Step 3: Add OCI Function Action

1. **Add OCI Function from Palette**
   - Drag "Oracle Cloud Infrastructure" from the right palette
   - Drop it after the trigger
   - Name it: `InvokeMigrationFunction`

2. **Configure Function Connection**
   - **Region**: Select your OCI region (e.g., `us-phoenix-1`)
   - **Compartment**: Browse and select the compartment containing your function
   - **Application**: Select `dbrx-to-atp-app`
   - **Function**: Select `dbrx-to-atp-migration`

3. **Configure Request**

   The function accepts parameters in JSON format. Here's what you need to configure:

   **Required Parameters (You MUST provide):**
   ```json
   {
     "share_name": "delta_sharing",
     "schema_name": "default",
     "table_name": "boston-housing"
   }
   ```

   **Optional Parameters (Override defaults):**
   ```json
   {
     "oracle_table_name": "boston_housing",  // Default: same as table_name
     "batch_size": 100,                       // Default: 100
     "limit_rows": 200                        // Default: null (all rows)
   }
   ```

   **Auto-Handled by Function (Don't pass these):**
   ```json
   {
     "delta_profile_base64": "...",          // ✅ Auto-loaded from /function/delta_share_profile.json
     "oracle_user": "...",                   // ✅ Auto-loaded from environment variable
     "oracle_password": "...",               // ✅ Auto-loaded from environment variable
     "oracle_dsn": "...",                    // ✅ Auto-loaded from environment variable
     "oracle_wallet_location": "/function/wallet",  // ✅ Hardcoded in function
     "oracle_wallet_password": null          // ✅ Not needed (extracted from wallet)
   }
   ```

   **Complete Request Schema for OIC:**
   ```json
   {
     "share_name": "",
     "schema_name": "",
     "table_name": "",
     "oracle_table_name": "",
     "batch_size": 100,
     "limit_rows": null
   }
   ```

4. **Configure Response**
   Define expected response:
   ```json
   {
     "status": "",
     "rows_migrated": 0,
     "total_rows_in_oracle": 0,
     "source": "",
     "destination": ""
   }
   ```

### Step 4: Map Request Data

1. **Click on Mapper** (before OCI Function action)

2. **Map ONLY These Fields from REST Trigger:**
   ```
   Left (Source - from trigger) → Right (Target - to function)

   share_name → share_name                   (REQUIRED)
   schema_name → schema_name                 (REQUIRED)
   table_name → table_name                   (REQUIRED)
   oracle_table_name → oracle_table_name     (OPTIONAL - defaults to table_name)
   batch_size → batch_size                   (OPTIONAL - defaults to 100)
   limit_rows → limit_rows                   (OPTIONAL - defaults to null)
   ```

3. **DO NOT Map These Fields** (automatically handled by function):
   ```
   ❌ delta_profile_base64     - Auto-loaded from Docker image
   ❌ oracle_user              - Auto-loaded from OCI Function configuration
   ❌ oracle_password          - Auto-loaded from OCI Function configuration
   ❌ oracle_dsn               - Auto-loaded from OCI Function configuration
   ❌ oracle_wallet_location   - Hardcoded as /function/wallet
   ❌ oracle_wallet_password   - Not needed
   ```

   **Why?** These are pre-configured when the function was deployed via GitHub Actions:
   - Delta Share profile is baked into the Docker image
   - Oracle credentials are set as OCI Function configuration variables
   - Oracle wallet is embedded in the Docker image

4. **Example Mapper Configuration:**

   **Minimal (only required fields):**
   ```
   Mapping Expression:
   share_name ← "delta_sharing"
   schema_name ← "default"
   table_name ← "boston-housing"
   ```

   **Full (with optional parameters):**
   ```
   Mapping Expression:
   share_name ← $RestTrigger.request.share_name
   schema_name ← $RestTrigger.request.schema_name
   table_name ← $RestTrigger.request.table_name
   oracle_table_name ← $RestTrigger.request.oracle_table_name
   batch_size ← $RestTrigger.request.batch_size
   limit_rows ← $RestTrigger.request.limit_rows
   ```

### Step 5: Map Response Data

1. **Click on Mapper** (after OCI Function action)
2. **Map Response Fields**:
   ```
   Left (Function Response) → Right (Integration Response)

   status → status
   rows_migrated → rows_migrated
   total_rows_in_oracle → total_rows_in_oracle
   source → source
   destination → destination
   ```

### Step 6: Add Error Handling

1. **Add Scope**
   - Wrap the OCI Function invocation in a Scope
   - Name: `MigrationScope`

2. **Add Fault Handler**
   - Click on Scope
   - Add "Fault Handlers"
   - Select "All Faults"

3. **Add Error Logging**
   - Inside fault handler, add "Assign" action
   - Create error response:
   ```xml
   <error>
     <status>failed</status>
     <message>$fault.message</message>
   </error>
   ```

### Step 7: Configure Integration Properties

1. **Click on hamburger menu** (top right)
2. **Select "Properties"**
3. **Add Configuration Properties**:
   ```
   Name: deltaProfileBase64
   Value: <base64-encoded-delta-share-profile>
   Type: String

   Name: oracleUser
   Value: ADMIN
   Type: String

   Name: oraclePassword
   Value: <your-password>
   Type: Password

   Name: oracleDsn
   Value: yourdb_high
   Type: String
   ```

### Step 8: Enable Tracing

1. **Click on hamburger menu**
2. **Select "Tracking"**
3. **Add Tracking Fields**:
   - `share_name`
   - `table_name`
   - `status`
   - `rows_migrated`

### Step 9: Activate Integration

1. **Click "Close"** to exit the designer
2. **Click "Activate"**
3. **Select Options**:
   - ✅ Enable tracing
   - ✅ Include payload
   - Click "Activate"

### Step 10: Test Integration

1. **Click on hamburger menu** on the activated integration
2. **Select "Run"**
3. **Provide Test Input**:
   ```json
   {
     "share_name": "delta_sharing",
     "schema_name": "default",
     "table_name": "boston-housing",
     "oracle_table_name": "boston_housing",
     "batch_size": 50,
     "limit_rows": 100
   }
   ```
4. **Click "Run Now"**
5. **Monitor Execution** in Activity Stream

## Example Integration Patterns

### Pattern 1: Scheduled Migration (Recommended)

Use OIC's Schedule adapter to run migrations periodically:

```
[Schedule Adapter] → [OCI Function] → [Notification]
  (every day 2 AM)
```

**Setup Steps:**
1. Create new integration with Schedule as trigger
2. Configure schedule:
   - **Frequency**: Daily, Hourly, Weekly, etc.
   - **Time**: Specific time (e.g., 2:00 AM)
   - **Timezone**: Your preferred timezone
3. Add OCI Function invocation
4. Add email notification for results
5. Activate

**Use Cases:**
- Daily data refresh from Databricks to ATP
- Hourly incremental updates
- Weekly full data sync

### Pattern 2: File-Triggered Migration

Trigger migration when a config file is uploaded to object storage:

```
[File Adapter] → [Parse Config] → [OCI Function] → [Email Result]
  (watch folder)
```

**Use Cases:**
- Upload CSV with list of tables to migrate
- Configuration-driven migrations
- Batch processing workflows

### Pattern 3: REST API with Validation

Expose REST API with input validation:

```
[REST Trigger] → [Validate Input] → [OCI Function] → [Log to Database] → [REST Response]
```

**Use Cases:**
- On-demand migration triggered by external systems
- Integration with CI/CD pipelines
- Manual testing and debugging

### Pattern 4: Multi-Table Migration

Loop through multiple tables:

```
[REST Trigger] → [For-Each Table] → [OCI Function] → [Aggregate Results] → [Response]
```

**Use Cases:**
- Migrate entire schema at once
- Bulk data operations
- Coordinated multi-table updates

## Complete Integration Example

Here's a complete integration flow:

```
┌─────────────────┐
│  REST Trigger   │ ← External system calls this
│  POST /migrate  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate Input  │ ← Check required fields
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lookup Config   │ ← Get credentials from lookup
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCI Function    │ ← Invoke dbrx-to-atp-migration
│ dbrx-to-atp     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────┐
│Success│  │Error │
└──┬──┘   └──┬───┘
   │         │
   ▼         ▼
┌─────────────────┐
│  Send Email     │ ← Notify result
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return Response │
└─────────────────┘
```

## Monitoring and Troubleshooting

### View Integration Runs
1. Navigate to "Monitoring" → "Integrations"
2. Click on your integration
3. View execution history

### Debug Failed Runs
1. Click on failed instance
2. View activity stream
3. Check each step's input/output
4. Download diagnostic logs if needed

### Common Issues

**Issue**: Function returns 401 Unauthorized
- **Cause**: Missing or incorrect IAM policies
- **Solution**: Add policy:
  ```
  Allow any-user to use fn-function in compartment <name> where ALL {request.principal.type='integration'}
  ```

**Issue**: Function timeout in OIC
- **Cause**: Function takes longer than OIC timeout (default 60s)
- **Solution**:
  - Increase batch size in function
  - Reduce limit_rows
  - Increase OIC connection timeout settings

**Issue**: Cannot find function in OIC
- **Cause**: Wrong region or compartment selected
- **Solution**: Verify function region matches OIC configuration

## Security Best Practices

1. **Never hardcode credentials** - Use OIC configuration or lookups
2. **Use OCI Vault** for sensitive data
3. **Implement proper error handling** to avoid exposing secrets in logs
4. **Enable SSL/TLS** for all connections
5. **Audit integration access** regularly
6. **Use least privilege** IAM policies
7. **Rotate credentials** periodically

## Performance Optimization

1. **Batch Processing**: Set appropriate `batch_size` (50-200 rows)
2. **Limit Rows**: Use `limit_rows` for testing, remove for production
3. **Parallel Processing**: Create multiple integrations for different tables
4. **Connection Pooling**: Reuse Oracle connections when possible
5. **Async Invocation**: For large migrations, use async patterns

## Quick Start: Create a Scheduled Integration

The fastest way to get started with automated data migration:

### 1. Create Scheduled Integration

```bash
# In OIC Console:
# 1. Integrations → Create → Schedule
# 2. Name: "Daily_DBRX_ATP_Sync"
# 3. Schedule: Daily at 2:00 AM
```

### 2. Add Function Invocation

```bash
# Drag "Oracle Cloud Infrastructure" adapter
# Configure:
#   - Region: us-phoenix-1
#   - Compartment: <your-compartment>
#   - Application: dbrx-to-atp-app
#   - Function: dbrx-to-atp-migration
```

### 3. Set Function Parameters

Use the mapper to set these values:

| Parameter | Value (Example) |
|-----------|----------------|
| `share_name` | `"delta_sharing"` |
| `schema_name` | `"default"` |
| `table_name` | `"boston-housing"` |
| `oracle_table_name` | `"boston_housing"` |
| `batch_size` | `100` |
| `limit_rows` | `null` (all rows) |
| `delta_profile_base64` | From configuration |
| `oracle_user` | From configuration |
| `oracle_password` | From configuration |
| `oracle_dsn` | From configuration |

### 4. Add Email Notification

```bash
# After function success:
# - Drag "Notification" adapter
# - Configure email with results
# - Subject: "DBRX to ATP Migration Completed"
# - Body: Include rows_migrated, status, etc.
```

### 5. Activate and Test

```bash
# Click "Activate"
# Enable tracing and payload logging
# Use "Submit Now" to test immediately
```

That's it! Your data will now sync automatically every day at 2 AM.

## Next Steps

- Set up monitoring and alerts
- Create parameterized migrations for multiple tables
- Implement retry logic for failed migrations
- Create dashboard for migration metrics
- Automate testing with OIC Test Framework
- Explore multi-table batch migrations

## Resources

- [OIC Functions Documentation](https://docs.oracle.com/en/cloud/paas/application-integration/integrations-user/invoke-oracle-cloud-infrastructure-functions-directly-integration-oci-function-action.html)
- [OIC Best Practices](https://docs.oracle.com/en/cloud/paas/application-integration/integration-design-best-practices.html)
- [Function Deployment Guide](DEPLOYMENT.md)
