# OIC Integration Guide - DBRX to ATP Function

This guide shows how to invoke the deployed OCI Function from Oracle Integration Cloud (OIC), based on the OIC Functions feature demonstration.

## Overview

Oracle Integration Cloud (OIC) provides native support for invoking OCI Functions directly from integrations. This allows you to create serverless data migration workflows that can be triggered from various sources (REST APIs, scheduled jobs, file uploads, etc.).

## Prerequisites

1. Deployed OCI Function (see [DEPLOYMENT.md](DEPLOYMENT.md))
2. OIC instance in the same tenancy
3. Function OCID and invoke endpoint (from CDKTF outputs)
4. Appropriate IAM policies

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

### Step 2: Add REST Trigger (Optional)

If you want to trigger the integration via REST API:

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

2. **Define Request Payload**
   Click "Request" tab and provide sample JSON:
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
   Click "Request" tab and provide the function input schema:
   ```json
   {
     "delta_profile_base64": "",
     "share_name": "",
     "schema_name": "",
     "table_name": "",
     "oracle_user": "",
     "oracle_password": "",
     "oracle_dsn": "",
     "oracle_wallet_location": "",
     "oracle_wallet_password": null,
     "batch_size": 100,
     "limit_rows": null,
     "oracle_table_name": ""
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
2. **Map Fields**:
   ```
   Left (Source - from trigger) → Right (Target - to function)

   share_name → share_name
   schema_name → schema_name
   table_name → table_name
   oracle_table_name → oracle_table_name
   batch_size → batch_size
   limit_rows → limit_rows
   ```

3. **Configure Credentials** (use one of these methods):

   **Option A: Hardcoded (Development Only)**
   ```
   delta_profile_base64 ← "base64-encoded-profile-content"
   oracle_user ← "ADMIN"
   oracle_password ← "YourPassword"
   oracle_dsn ← "yourdb_high"
   oracle_wallet_location ← "/tmp/wallet"
   ```

   **Option B: Using OIC Configuration** (Recommended)
   - Create integration properties for sensitive values
   - Map them in the mapper:
   ```
   delta_profile_base64 ← $deltaProfileBase64Config
   oracle_user ← $oracleUserConfig
   oracle_password ← $oraclePasswordConfig
   oracle_dsn ← $oracleDsnConfig
   ```

   **Option C: Using Lookups** (Best for Production)
   - Create lookup tables for configuration
   - Use lookup() function to retrieve values

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

### Pattern 1: Scheduled Migration

Use OIC's Schedule adapter to run migrations periodically:

```
[Schedule Adapter] → [OCI Function] → [Notification]
  (every day 2 AM)
```

### Pattern 2: File-Triggered Migration

Trigger migration when a config file is uploaded to object storage:

```
[File Adapter] → [Parse Config] → [OCI Function] → [Email Result]
  (watch folder)
```

### Pattern 3: REST API with Validation

Expose REST API with input validation:

```
[REST Trigger] → [Validate Input] → [OCI Function] → [Log to Database] → [REST Response]
```

### Pattern 4: Multi-Table Migration

Loop through multiple tables:

```
[REST Trigger] → [For-Each Table] → [OCI Function] → [Aggregate Results] → [Response]
```

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

## Next Steps

- Set up monitoring and alerts
- Create parameterized migrations for multiple tables
- Implement retry logic for failed migrations
- Create dashboard for migration metrics
- Automate testing with OIC Test Framework

## Resources

- [OIC Functions Documentation](https://docs.oracle.com/en/cloud/paas/application-integration/integrations-user/invoke-oracle-cloud-infrastructure-functions-directly-integration-oci-function-action.html)
- [OIC Best Practices](https://docs.oracle.com/en/cloud/paas/application-integration/integration-design-best-practices.html)
- [Function Deployment Guide](DEPLOYMENT.md)
