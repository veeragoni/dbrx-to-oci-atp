# GitHub Secrets Setup Guide

GitHub Secrets need to be created manually in your repository settings. Here's how:

## 📍 Where to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

Or direct URL:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
```

## 🔑 Required Secrets

### 1. ORACLE_WALLET_BASE64

**Value:** Base64-encoded zip of your Oracle wallet

**How to get it:**
```bash
cd /Users/veeragoni/Projects/dbrx-to-oci-atp
./scripts/create_wallet_secret.sh
```

Copy the output and paste as the secret value.

---

### 2. OCIR_USERNAME

**Value:**
```
hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com
```

(Format: `<tenancy-namespace>/<idcs-or-oam>/username`)

---

### 3. OCIR_TOKEN

**Value:** Your OCI Auth Token

**How to get it:**
1. Go to OCI Console
2. Click your profile icon (top right) → **User Settings**
3. Click **Auth Tokens** (left sidebar)
4. Click **Generate Token**
5. Name it: `github-actions`
6. Copy the token (you won't see it again!)
7. Paste as the secret value

---

### 4. OCI_USER_OCID

**Value:** Your OCI user OCID

**How to get it:**
```bash
# From your infrastructure/.env file
cat infrastructure/.env | grep OCI_USER_OCID
```

Copy the value (looks like: `ocid1.user.oc1..aaaaaaaajxqfok3...`)

---

### 5. OCI_TENANCY_OCID

**Value:** Your OCI tenancy OCID

**How to get it:**
```bash
# From your infrastructure/.env file
cat infrastructure/.env | grep OCI_TENANCY_OCID
```

Copy the value (looks like: `ocid1.tenancy.oc1..aaaaaaaab5xalljjh...`)

---

### 6. OCI_FINGERPRINT

**Value:** Your OCI API key fingerprint

**How to get it:**
```bash
# From your infrastructure/.env file
cat infrastructure/.env | grep OCI_FINGERPRINT
```

Copy the value (looks like: `81:51:b5:17:ad:ed:0e:b9:8d:66:ca:6f:f7:bb:f5:cc`)

---

### 7. OCI_PRIVATE_KEY

**Value:** Content of your OCI API private key file

**How to get it:**
```bash
# From your infrastructure/.env file, get the path
cat infrastructure/.env | grep OCI_PRIVATE_KEY_PATH

# Then read the private key file
cat /Users/veeragoni/.oci/oci_api_key.pem
```

Copy the **entire content** including the header and footer:
```
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
...
-----END PRIVATE KEY-----
```

---

## 📋 Quick Setup Checklist

```bash
# 1. Create wallet secret
cd /Users/veeragoni/Projects/dbrx-to-oci-atp
./scripts/create_wallet_secret.sh
# Copy output → Add as ORACLE_WALLET_BASE64

# 2. Get OCI credentials
cat infrastructure/.env
# Copy each value to corresponding GitHub secret

# 3. Get OCIR username
echo "hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com"
# Copy → Add as OCIR_USERNAME

# 4. Generate OCI Auth Token
# Go to OCI Console → Profile → User Settings → Auth Tokens
# Generate new token → Copy → Add as OCIR_TOKEN

# 5. Get private key content
cat /Users/veeragoni/.oci/oci_api_key.pem
# Copy entire content → Add as OCI_PRIVATE_KEY
```

## ✅ Verify Setup

After adding all secrets, go to:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
```

You should see 7 secrets:
- ✅ ORACLE_WALLET_BASE64
- ✅ OCIR_USERNAME
- ✅ OCIR_TOKEN
- ✅ OCI_USER_OCID
- ✅ OCI_TENANCY_OCID
- ✅ OCI_FINGERPRINT
- ✅ OCI_PRIVATE_KEY

## 🚀 Test the Workflow

Once secrets are added:

1. Push code to GitHub:
   ```bash
   git push origin main
   ```

2. GitHub Actions will automatically:
   - Build Docker image on x86_64 (no NumPy errors!)
   - Push to OCIR
   - Update OCI Function

3. Check workflow status:
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO/actions
   ```

## 🔒 Security Notes

- ✅ Secrets are encrypted by GitHub
- ✅ Secrets are not shown in logs
- ✅ Only accessible during workflow execution
- ✅ Cannot be read after creation (only updated)

## ❓ Troubleshooting

**Secret not working?**
- Make sure there are no extra spaces or newlines
- For private key, include the BEGIN/END lines
- For wallet, make sure it's valid base64

**Workflow fails?**
- Check Actions tab for detailed logs
- Verify all 7 secrets are created
- Ensure OCIR auth token is valid (not expired)

---

**Need help?** See the workflow file: `.github/workflows/build-and-push.yml`
