# Complete Deployment Steps - All Fixes Applied

## Summary of Changes Made

### 1. **Dockerfile Updated**
- ✅ Added wallet copy to Docker image
- ✅ Set TNS_ADMIN environment variable
- ✅ Building for x86_64 platform (required by OCI Functions)

### 2. **Test Script Updated**
- ✅ Correct payload format matching function expectations
- ✅ Uses actual Delta Share info: `delta_sharing.default.COVID_19_NYT`
- ✅ Includes wallet location in container: `/function/wallet`

### 3. **Infrastructure**
- ✅ Removed policy creation (requires admin permissions)
- ✅ Fixed TypeScript imports for CDKTF

## Before You Deploy

### Step 1: Create Target Table in ATP

Connect to your ATP database and run:

```sql
CREATE TABLE MIGRATED_DATA (
    date_val DATE,
    county VARCHAR2(100),
    state VARCHAR2(100),
    fips NUMBER,
    cases NUMBER,
    deaths NUMBER
);
```

Or use the provided script:
```bash
sqlplus ADMIN/wR66up2ptVyyM9F4@ndg3d3lxz4esodqc_high @create_test_table.sql
```

### Step 2: Rebuild and Redeploy Function

```bash
cd /Users/veeragoni/Projects/dbrx-to-oci-atp/infrastructure
./deploy.sh
```

This will:
1. Build Docker image for x86_64 with wallet included
2. Push to OCIR (say 'y' when prompted since image changed)
3. Update OCI Functions deployment

### Step 3: Test the Function

```bash
cd /Users/veeragoni/Projects/dbrx-to-oci-atp
python test_function.py
```

## Expected Result

If everything works, you should see:

```json
{
  "status": "success",
  "rows_migrated": 10,
  "total_rows_in_oracle": 10,
  "source": "delta_sharing.default.COVID_19_NYT",
  "destination": "MIGRATED_DATA"
}
```

## Troubleshooting

If function still fails:
1. Check function logs: `python check_logs.py`
2. Verify wallet is in container: Check deployment logs
3. Test ATP connection separately
4. Check OCI Console → Functions → Logs tab

## Key Changes to Review

### Dockerfile (`/function/Dockerfile`)
- Line 26: Copies wallet directory
- Line 30: Sets TNS_ADMIN for Oracle connectivity

### Test Script (`test_function.py`)
- Lines 44-56: Correct payload structure
- Uses real Delta Share: `delta_sharing.default.COVID_19_NYT`
- Wallet location: `/function/wallet`

### Infrastructure (`infrastructure/main.ts`)
- Lines 109-114: Policy creation commented out (manual setup required)
