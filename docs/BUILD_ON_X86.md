# Building Docker Image on x86_64 Platform

The NumPy cross-compilation issue can be solved by building on a native x86_64 machine.

## Option 1: Use OCI Cloud Shell (Easiest!)

OCI Cloud Shell is x86_64 and has Docker pre-installed.

1. **Open OCI Cloud Shell** in the OCI Console (top right icon)

2. **Upload your function code:**
```bash
# In Cloud Shell
mkdir -p dbrx-function
cd dbrx-function
```

3. **Upload files** using the Cloud Shell upload button:
   - `Dockerfile`
   - `func.py`
   - `requirements.txt`
   - `Wallet_NDG3D3LXZ4ESODQC/` (entire folder)

4. **Login to OCIR:**
```bash
docker login iad.ocir.io
# Username: hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com
# Password: <your-auth-token>
```

5. **Build and push:**
```bash
docker build -t iad.ocir.io/hpctraininglab/atp-repo:latest .
docker push iad.ocir.io/hpctraininglab/atp-repo:latest
```

6. **Update function:**
```bash
oci fn function update \
  --function-id ocid1.fnfunc.oc1.iad.amaaaaaa52tswuaanqz25ylbc5cv5j6u3l2l6rdyrtzpoij77j3rgu7bk6sq \
  --image iad.ocir.io/hpctraininglab/atp-repo:latest \
  --force
```

## Option 2: Use GitHub Actions (Automated)

Push your code to GitHub and the workflow will automatically build and deploy.

See `.github/workflows/build-and-push.yml`

Required GitHub Secrets:
- `OCIR_USERNAME`: hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com
- `OCIR_TOKEN`: Your OCIR auth token
- `OCI_USER_OCID`
- `OCI_TENANCY_OCID`
- `OCI_FINGERPRINT`
- `OCI_PRIVATE_KEY`

## Option 3: Use AWS EC2 Free Tier x86_64

Launch a t2.micro (x86_64) instance, install Docker, and build there.

## Why This Is Needed

Cross-compiling NumPy/Pandas from ARM (Apple Silicon) to x86_64 using QEMU emulation causes:
```
NumPy internal error: unable to get format_options context variable
```

Building natively on x86_64 avoids this issue completely.
