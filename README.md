# Databricks to Oracle ATP Data Migration Tool

Migrate data from Databricks to Oracle Autonomous Transaction Processing (ATP) with support for both direct connection and Delta Sharing.

## Data Flow

### Method 1: Direct Connection
```mermaid
graph LR
    A[Databricks] -->|SQL Connector| B[Python Script]
    B -->|OracleDB Driver| C[Oracle ATP]
```

### Method 2: Delta Sharing
```mermaid
graph LR
    A[Databricks Delta Share] -->|Delta Sharing Protocol| B[Python Script]
    B -->|OracleDB Driver| C[Oracle ATP]
```

## Quick Start

```bash
# 1. Clone and navigate to project
cd dbrx-to-oci-atp

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run the script
python src/dbrx-data.py
```

## Configuration

### 1. Oracle ATP Setup

Download your ATP wallet from Oracle Cloud Console:
- Navigate to your ATP database → **DB Connection** → **Download Wallet**
- Extract to project directory (e.g., `./Wallet_myatp`)

### 2. Environment Variables

Update `.env` with your credentials:

```bash
# For Direct Databricks Connection
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=your-access-token

# For Delta Sharing (alternative to direct connection)
DELTA_SHARE_PROFILE_PATH=./config.share
DELTA_SHARE_NAME=your_share_name
DELTA_SCHEMA_NAME=your_schema_name
DELTA_TABLE_NAME=your_table_name

# Oracle ATP Configuration
ORACLE_USER=ADMIN
ORACLE_PASSWORD=your-password
ORACLE_DSN=your_tns_name_high
ORACLE_WALLET_LOCATION=./Wallet_myatp
ORACLE_WALLET_PASSWORD=
```

## Usage

### Method 1: Direct Databricks Connection

Edit `src/dbrx-data.py` and uncomment:

```python
# Create table and insert data in Databricks
create_table()
insert_synthetic_data(num_rows=1000, start_id=1)

# Create table in Oracle ATP
create_oracle_table(oracle_user, oracle_password, oracle_dsn,
                   oracle_wallet_location, oracle_wallet_password)

# Migrate from Databricks to Oracle ATP
migrate_to_oracle(oracle_user, oracle_password, oracle_dsn,
                 oracle_wallet_location, oracle_wallet_password)
```

### Method 2: Delta Sharing (No Databricks Credentials Required)

Edit `src/dbrx-data.py` and uncomment:

```python
# Create table in Oracle ATP
create_oracle_table(oracle_user, oracle_password, oracle_dsn,
                   oracle_wallet_location, oracle_wallet_password)

# Migrate from Delta Share to Oracle ATP
migrate_to_oracle_delta_share(
    delta_profile_path, delta_share_name, delta_schema_name, delta_table_name,
    oracle_user, oracle_password, oracle_dsn,
    oracle_wallet_location, oracle_wallet_password
)
```

### Run the Script

```bash
python src/dbrx-data.py
```

## Demo: Public Delta Share

Test the migration with a public dataset (no Databricks credentials needed):

```python
# Uses included demo.share for Boston Housing dataset
python src/dbrx-data.py  # Already configured in script
```

This migrates 200 rows from the public Boston Housing dataset to your Oracle ATP instance.

## Project Structure

```
dbrx-to-oci-atp/
├── src/
│   ├── dbrx-data.py                 # Main migration script
│   ├── test_delta_sharing.py        # Delta sharing tests
│   └── test_delta_sharing_simple.py # Simple examples
├── demo.share                        # Public demo config
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
└── README.md                         # This file
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `DPY-4027: no configuration directory` | Verify wallet location path is correct |
| `DPY-6000: Listener refused connection` | Check TNS name matches `tnsnames.ora` |
| `ORA-12506` | Ensure correct TNS name for TCPS connections |
| Import errors | Run `pip install -r requirements.txt` |

## Features

- ✅ Direct Databricks SQL connection
- ✅ Delta Sharing protocol support
- ✅ Batch processing for performance
- ✅ Progress tracking
- ✅ Automatic data type conversion
- ✅ Public demo dataset included
