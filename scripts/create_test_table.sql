-- Create a simple test table for COVID_19_NYT data
-- This matches the schema of the Delta Share table

DROP TABLE MIGRATED_DATA PURGE;

CREATE TABLE MIGRATED_DATA (
    date_val DATE,
    county VARCHAR2(100),
    state VARCHAR2(100),
    fips NUMBER,
    cases NUMBER,
    deaths NUMBER
);

-- Grant necessary privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON MIGRATED_DATA TO ADMIN;

SELECT 'Table MIGRATED_DATA created successfully' AS status FROM dual;
