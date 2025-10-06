from databricks import sql
import os
from faker import Faker
import random
import oracledb
from dotenv import load_dotenv
import delta_sharing

# Load environment variables from .env file
load_dotenv()

fake = Faker()

def get_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_ACCESS_TOKEN")
    )

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscription_transactions (
            transaction_id INT,
            user_id STRING,
            user_name STRING,
            user_email STRING,
            subscription_plan STRING,
            billing_cycle STRING,
            amount DECIMAL(10, 2),
            currency STRING,
            payment_method STRING,
            transaction_date TIMESTAMP,
            start_date DATE,
            end_date DATE,
            status STRING,
            is_renewal BOOLEAN,
            discount_applied DECIMAL(5, 2),
            country STRING
        )
    """)

    print("Table created successfully")
    cursor.close()
    connection.close()

def insert_synthetic_data(num_rows=1000, start_id=1):
    connection = get_connection()
    cursor = connection.cursor()

    subscription_plans = ['Basic', 'Premium', 'Pro', 'Enterprise', 'Starter', 'Ultimate']
    billing_cycles = ['monthly', 'quarterly', 'yearly']
    statuses = ['completed', 'pending', 'failed', 'refunded']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'apple_pay', 'google_pay']
    currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']

    plan_prices = {
        'Basic': {'monthly': 9.99, 'quarterly': 26.99, 'yearly': 99.99},
        'Premium': {'monthly': 19.99, 'quarterly': 53.99, 'yearly': 199.99},
        'Pro': {'monthly': 29.99, 'quarterly': 80.99, 'yearly': 299.99},
        'Enterprise': {'monthly': 99.99, 'quarterly': 269.99, 'yearly': 999.99},
        'Starter': {'monthly': 4.99, 'quarterly': 13.49, 'yearly': 49.99},
        'Ultimate': {'monthly': 49.99, 'quarterly': 134.99, 'yearly': 499.99}
    }

    print(f"Inserting {num_rows} rows of synthetic data...")

    for i in range(start_id, start_id + num_rows):
        plan = random.choice(subscription_plans)
        cycle = random.choice(billing_cycles)
        amount = plan_prices[plan][cycle]
        is_renewal = random.choice([True, False])
        discount = round(random.uniform(0, 25), 2) if random.random() > 0.7 else 0.00

        transaction_date = fake.date_time_between(start_date='-1y', end_date='now')
        start_date = transaction_date.date()

        # Calculate end date based on billing cycle
        if cycle == 'monthly':
            days = 30
        elif cycle == 'quarterly':
            days = 90
        else:
            days = 365

        from datetime import timedelta
        end_date = start_date + timedelta(days=days)

        # Apply discount
        final_amount = round(amount * (1 - discount/100), 2)

        cursor.execute(
            """
            INSERT INTO subscription_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                i,
                fake.uuid4(),
                fake.name(),
                fake.email(),
                plan,
                cycle,
                final_amount,
                random.choice(currencies),
                random.choice(payment_methods),
                transaction_date,
                start_date,
                end_date,
                random.choice(statuses),
                is_renewal,
                discount,
                fake.country()
            )
        )
        if (i - start_id + 1) % 100 == 0:
            print(f"Inserted {i - start_id + 1} rows...")

    print("Data insertion complete!")
    cursor.close()
    connection.close()

def read_data(limit=5):
    connection = get_connection()
    cursor = connection.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM subscription_transactions")
    count = cursor.fetchone()
    print(f"Total rows in table: {count[0]}")

    # Get sample data
    cursor.execute(f"SELECT * FROM subscription_transactions LIMIT {limit}")
    print(f"\nSample data (showing {limit} rows):")
    for row in cursor.fetchall():
        print(row)

    cursor.close()
    connection.close()

def read_data_delta_share(profile_path, share_name, schema_name, table_name, limit=5):
    """
    Read data using Delta Sharing
    Args:
        profile_path: Path to Delta Sharing profile file (.share)
        share_name: Name of the share
        schema_name: Name of the schema
        table_name: Name of the table
        limit: Number of rows to display (default: 5)
    """
    # Create Delta Sharing client
    client = delta_sharing.SharingClient(profile_path)

    # Construct table URL
    table_url = f"{profile_path}#{share_name}.{schema_name}.{table_name}"

    # Load table as pandas DataFrame
    df = delta_sharing.load_as_pandas(table_url)

    # Get total count
    total_rows = len(df)
    print(f"Total rows in table: {total_rows}")

    # Display sample data
    print(f"\nSample data (showing {min(limit, total_rows)} rows):")
    print(df.head(limit))

    return df

def migrate_to_oracle_delta_share(profile_path, share_name, schema_name, table_name,
                                   oracle_user, oracle_password, oracle_dsn,
                                   wallet_location=None, wallet_password=None, batch_size=100):
    """
    Read data from Delta Share and insert into Oracle ATP
    Args:
        profile_path: Path to Delta Sharing profile file (.share)
        share_name: Name of the share
        schema_name: Name of the schema
        table_name: Name of the table
        oracle_user: Oracle username
        oracle_password: Oracle password
        oracle_dsn: Oracle connection string
        wallet_location: Path to wallet directory (optional)
        wallet_password: Wallet password (optional)
        batch_size: Number of rows to insert per batch
    """
    # Load data from Delta Share
    table_url = f"{profile_path}#{share_name}.{schema_name}.{table_name}"
    df = delta_sharing.load_as_pandas(table_url)

    total_rows = len(df)
    print(f"Total rows to migrate from Delta Share: {total_rows}")

    # Connect to Oracle
    oracle_conn = get_oracle_connection(oracle_user, oracle_password, oracle_dsn, wallet_location, wallet_password)
    oracle_cursor = oracle_conn.cursor()

    rows_inserted = 0
    batch = []

    for idx, row in df.iterrows():
        # Convert boolean to number for Oracle if needed
        is_renewal = 1 if row.get('is_renewal', False) else 0

        batch.append((
            int(row.get('transaction_id', 0)),
            str(row.get('user_id', '')),
            str(row.get('user_name', '')),
            str(row.get('user_email', '')),
            str(row.get('subscription_plan', '')),
            str(row.get('billing_cycle', '')),
            float(row.get('amount', 0.0)),
            str(row.get('currency', '')),
            str(row.get('payment_method', '')),
            row.get('transaction_date'),
            row.get('start_date'),
            row.get('end_date'),
            str(row.get('status', '')),
            is_renewal,
            float(row.get('discount_applied', 0.0)),
            str(row.get('country', ''))
        ))

        if len(batch) >= batch_size:
            oracle_cursor.executemany(
                """
                INSERT INTO subscription_transactions
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16)
                """,
                batch
            )
            oracle_conn.commit()
            rows_inserted += len(batch)
            print(f"Inserted {rows_inserted} rows...")
            batch = []

    # Insert remaining rows
    if batch:
        oracle_cursor.executemany(
            """
            INSERT INTO subscription_transactions
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16)
            """,
            batch
        )
        oracle_conn.commit()
        rows_inserted += len(batch)

    print(f"Migration complete! Total rows inserted: {rows_inserted}")

    # Verify count in Oracle
    oracle_cursor.execute("SELECT COUNT(*) FROM subscription_transactions")
    oracle_count = oracle_cursor.fetchone()[0]
    print(f"Verified rows in Oracle: {oracle_count}")

    oracle_cursor.close()
    oracle_conn.close()

def get_oracle_connection(user, password, dsn, wallet_location=None, wallet_password=None):
    """
    Connect to Oracle ATP database
    Args:
        user: Oracle username
        password: Oracle password
        dsn: Connection string (TNS name, Easy Connect, or service name)
        wallet_location: Path to wallet directory (optional, for ATP with wallet)
        wallet_password: Wallet password (optional)
    """
    if wallet_location:
        # For ATP with wallet
        return oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=wallet_password
        )
    else:
        # For regular connection or TLS without wallet
        return oracledb.connect(user=user, password=password, dsn=dsn)

def create_oracle_table(user, password, dsn, wallet_location=None, wallet_password=None):
    """Create the subscription_transactions table in Oracle ATP"""
    conn = get_oracle_connection(user, password, dsn, wallet_location, wallet_password)
    cursor = conn.cursor()

    # Drop table if exists
    try:
        cursor.execute("DROP TABLE subscription_transactions")
        print("Existing table dropped")
    except:
        pass

    # Create table
    cursor.execute("""
        CREATE TABLE subscription_transactions (
            transaction_id NUMBER(10),
            user_id VARCHAR2(100),
            user_name VARCHAR2(200),
            user_email VARCHAR2(200),
            subscription_plan VARCHAR2(50),
            billing_cycle VARCHAR2(20),
            amount NUMBER(10, 2),
            currency VARCHAR2(10),
            payment_method VARCHAR2(50),
            transaction_date TIMESTAMP,
            start_date DATE,
            end_date DATE,
            status VARCHAR2(20),
            is_renewal NUMBER(1),
            discount_applied NUMBER(5, 2),
            country VARCHAR2(100)
        )
    """)

    conn.commit()
    print("Oracle table created successfully")
    cursor.close()
    conn.close()

def migrate_to_oracle(user, password, dsn, wallet_location=None, wallet_password=None, batch_size=100):
    """
    Read data from Databricks and insert into Oracle ATP
    Args:
        user: Oracle username
        password: Oracle password
        dsn: Oracle connection string
        wallet_location: Path to wallet directory (optional)
        wallet_password: Wallet password (optional)
        batch_size: Number of rows to insert per batch
    """
    # Connect to Databricks
    dbrx_conn = get_connection()
    dbrx_cursor = dbrx_conn.cursor()

    # Connect to Oracle
    oracle_conn = get_oracle_connection(user, password, dsn, wallet_location, wallet_password)
    oracle_cursor = oracle_conn.cursor()

    # Get total count
    dbrx_cursor.execute("SELECT COUNT(*) FROM subscription_transactions")
    total_rows = dbrx_cursor.fetchone()[0]
    print(f"Total rows to migrate: {total_rows}")

    # Fetch and insert in batches
    dbrx_cursor.execute("SELECT * FROM subscription_transactions")

    rows_inserted = 0
    batch = []

    for row in dbrx_cursor:
        # Convert boolean to number for Oracle
        is_renewal = 1 if row[13] else 0

        batch.append((
            row[0],   # transaction_id
            row[1],   # user_id
            row[2],   # user_name
            row[3],   # user_email
            row[4],   # subscription_plan
            row[5],   # billing_cycle
            row[6],   # amount
            row[7],   # currency
            row[8],   # payment_method
            row[9],   # transaction_date
            row[10],  # start_date
            row[11],  # end_date
            row[12],  # status
            is_renewal,  # is_renewal (converted to number)
            row[14],  # discount_applied
            row[15]   # country
        ))

        if len(batch) >= batch_size:
            oracle_cursor.executemany(
                """
                INSERT INTO subscription_transactions
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16)
                """,
                batch
            )
            oracle_conn.commit()
            rows_inserted += len(batch)
            print(f"Inserted {rows_inserted} rows...")
            batch = []

    # Insert remaining rows
    if batch:
        oracle_cursor.executemany(
            """
            INSERT INTO subscription_transactions
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16)
            """,
            batch
        )
        oracle_conn.commit()
        rows_inserted += len(batch)

    print(f"Migration complete! Total rows inserted: {rows_inserted}")

    # Verify count in Oracle
    oracle_cursor.execute("SELECT COUNT(*) FROM subscription_transactions")
    oracle_count = oracle_cursor.fetchone()[0]
    print(f"Verified rows in Oracle: {oracle_count}")

    dbrx_cursor.close()
    dbrx_conn.close()
    oracle_cursor.close()
    oracle_conn.close()

def create_boston_housing_table(user, password, dsn, wallet_location=None, wallet_password=None):
    """Create boston_housing table in Oracle ATP"""
    conn = get_oracle_connection(user, password, dsn, wallet_location, wallet_password)
    cursor = conn.cursor()

    # Drop table if exists
    try:
        cursor.execute("DROP TABLE boston_housing")
        print("Existing boston_housing table dropped")
    except:
        pass

    # Create table
    cursor.execute("""
        CREATE TABLE boston_housing (
            id NUMBER(10),
            crim NUMBER(10, 5),
            zn NUMBER(10, 2),
            indus NUMBER(10, 2),
            chas NUMBER(1),
            nox NUMBER(10, 3),
            rm NUMBER(10, 3),
            age NUMBER(10, 2),
            dis NUMBER(10, 4),
            rad NUMBER(10),
            tax NUMBER(10),
            ptratio NUMBER(10, 1),
            black_index NUMBER(10, 2),
            lstat NUMBER(10, 2),
            medv NUMBER(10, 1)
        )
    """)

    conn.commit()
    print("Boston housing table created successfully")
    cursor.close()
    conn.close()

def migrate_boston_housing_to_oracle(profile_path, share_name, schema_name, table_name,
                                     oracle_user, oracle_password, oracle_dsn,
                                     wallet_location=None, wallet_password=None,
                                     limit_rows=200, batch_size=50):
    """
    Migrate Boston Housing data from public Delta Share to Oracle ATP
    """
    # Load data from Delta Share
    table_url = f"{profile_path}#{share_name}.{schema_name}.{table_name}"
    df = delta_sharing.load_as_pandas(table_url, limit=limit_rows)

    total_rows = len(df)
    print(f"Total rows to migrate from Delta Share (Boston Housing): {total_rows}")

    # Connect to Oracle
    oracle_conn = get_oracle_connection(oracle_user, oracle_password, oracle_dsn, wallet_location, wallet_password)
    oracle_cursor = oracle_conn.cursor()

    rows_inserted = 0
    batch = []

    for idx, row in df.iterrows():
        batch.append((
            int(row.get('ID', idx)),
            float(row.get('crim', 0.0)),
            float(row.get('zn', 0.0)),
            float(row.get('indus', 0.0)),
            int(row.get('chas', 0)),
            float(row.get('nox', 0.0)),
            float(row.get('rm', 0.0)),
            float(row.get('age', 0.0)),
            float(row.get('dis', 0.0)),
            int(row.get('rad', 0)),
            int(row.get('tax', 0)),
            float(row.get('ptratio', 0.0)),
            float(row.get('black', 0.0)),
            float(row.get('lstat', 0.0)),
            float(row.get('medv', 0.0))
        ))

        if len(batch) >= batch_size:
            oracle_cursor.executemany(
                """
                INSERT INTO boston_housing
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)
                """,
                batch
            )
            oracle_conn.commit()
            rows_inserted += len(batch)
            print(f"Inserted {rows_inserted} rows...")
            batch = []

    # Insert remaining rows
    if batch:
        oracle_cursor.executemany(
            """
            INSERT INTO boston_housing
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)
            """,
            batch
        )
        oracle_conn.commit()
        rows_inserted += len(batch)

    print(f"Migration complete! Total rows inserted: {rows_inserted}")

    # Verify count in Oracle
    oracle_cursor.execute("SELECT COUNT(*) FROM boston_housing")
    oracle_count = oracle_cursor.fetchone()[0]
    print(f"Verified rows in Oracle: {oracle_count}")

    oracle_cursor.close()
    oracle_conn.close()

if __name__ == "__main__":
    # Uncomment the operations you want to perform

    # ===== Method 1: Direct Databricks Connection =====
    # create_table()  # Run once to create the table
    # insert_synthetic_data(num_rows=1000, start_id=1)  # Insert data
    # read_data(limit=5)  # Read and display data

    # ===== Method 2: Delta Sharing (Read data without direct connection) =====
    # delta_profile_path = os.getenv("DELTA_SHARE_PROFILE_PATH")  # Path to .share file
    # delta_share_name = os.getenv("DELTA_SHARE_NAME")
    # delta_schema_name = os.getenv("DELTA_SCHEMA_NAME")
    # delta_table_name = os.getenv("DELTA_TABLE_NAME")
    #
    # read_data_delta_share(delta_profile_path, delta_share_name, delta_schema_name, delta_table_name, limit=5)

    # ===== Oracle ATP Migration - Direct Connection =====
    # oracle_user = os.getenv("ORACLE_USER")
    # oracle_password = os.getenv("ORACLE_PASSWORD")
    # oracle_dsn = os.getenv("ORACLE_DSN")
    # oracle_wallet_location = os.getenv("ORACLE_WALLET_LOCATION")
    # oracle_wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")  # Usually None
    #
    # create_oracle_table(oracle_user, oracle_password, oracle_dsn, oracle_wallet_location, oracle_wallet_password)
    # migrate_to_oracle(oracle_user, oracle_password, oracle_dsn, oracle_wallet_location, oracle_wallet_password, batch_size=100)

    # ===== Oracle ATP Migration - From Delta Share =====
    # migrate_to_oracle_delta_share(
    #     delta_profile_path, delta_share_name, delta_schema_name, delta_table_name,
    #     oracle_user, oracle_password, oracle_dsn,
    #     oracle_wallet_location, oracle_wallet_password, batch_size=100
    # )

    # ===== EXAMPLE: Migrate Public Boston Housing Data to Oracle =====
    # This uses the public Databricks Delta Share demo
    public_profile_path = "./demo.share"  # Uses public demo share
    oracle_user = os.getenv("ORACLE_USER")
    oracle_password = os.getenv("ORACLE_PASSWORD")
    oracle_dsn = os.getenv("ORACLE_DSN")
    oracle_wallet_location = os.getenv("ORACLE_WALLET_LOCATION")
    oracle_wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")

    # Step 1: Create boston_housing table in Oracle
    create_boston_housing_table(oracle_user, oracle_password, oracle_dsn, oracle_wallet_location, oracle_wallet_password)

    # Step 2: Migrate 200 rows from public Delta Share to Oracle
    migrate_boston_housing_to_oracle(
        public_profile_path, "delta_sharing", "default", "boston-housing",
        oracle_user, oracle_password, oracle_dsn,
        oracle_wallet_location, oracle_wallet_password,
        limit_rows=200, batch_size=50
    )