# Security Checklist - Prevent Secrets from Being Committed

## ✅ Files Protected by .gitignore

The following sensitive files are **automatically ignored** and will NOT be committed:

### Credentials & Secrets
- ✅ `.env` - Contains Oracle passwords, Delta Share tokens
- ✅ `infrastructure/.env` - Contains OCI credentials
- ✅ `*.share` - Contains Delta Share bearer tokens
- ✅ `*.pem`, `*.key` - OCI private keys

### Oracle Wallet (Database Credentials)
- ✅ `Wallet_*/` - All wallet directories
- ✅ `function/Wallet_*/` - Wallet in function directory
- ✅ `*.sso`, `*.p12`, `*.jks` - Wallet files
- ✅ `tnsnames.ora`, `sqlnet.ora` - Wallet config files

### Generated/Temporary Files
- ✅ `infrastructure/cdktf.out/` - CDKTF output (may contain OCIDs)
- ✅ `infrastructure/.terraform/` - Terraform state
- ✅ `infrastructure/terraform.tfstate*` - May contain passwords

## ⚠️ Before Committing - Double Check

Run these commands to verify no secrets will be committed:

```bash
# Check what files will be committed
git status

# Verify sensitive files are ignored
git check-ignore -v .env demo.share Wallet_NDG3D3LXZ4ESODQC/

# Search for potential secrets in tracked files
git grep -i "password\|secret\|token\|bearer"
```

## 🔒 For GitHub Actions

To use GitHub Actions, you need to add these secrets:

### Required GitHub Secrets

1. **ORACLE_WALLET_BASE64** - Base64-encoded wallet zip
   ```bash
   ./create_wallet_secret.sh
   ```
   Copy the output and add to GitHub Secrets.

2. **OCIR_USERNAME**
   ```
   hpctraininglab/oracleidentitycloudservice/suresh.veeragoni@oracle.com
   ```

3. **OCIR_TOKEN** - Your OCI auth token

4. **OCI_USER_OCID** - From .env

5. **OCI_TENANCY_OCID** - From .env

6. **OCI_FINGERPRINT** - From .env

7. **OCI_PRIVATE_KEY** - Content of your .pem file

### Adding Secrets to GitHub

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click "New repository secret"
3. Add each secret above

## 🚫 Never Commit These

- Passwords, API keys, tokens
- Private keys (.pem files)
- Oracle wallets
- .env files
- Delta Share profiles with tokens

## ✅ Safe to Commit

- Code files (*.py, *.ts, *.sh)
- Dockerfiles
- Requirements.txt
- README files
- Example files (*.example)
- .gitignore itself

## 🔍 If You Accidentally Commit Secrets

If you accidentally commit secrets:

1. **Immediately rotate the credentials** (generate new tokens/passwords)
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch PATH/TO/FILE" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```
3. Consider the secret compromised - change it everywhere

## 📝 Pre-Commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
if git diff --cached --name-only | grep -E '\.env$|\.pem$|Wallet_|\.share$'; then
    echo "ERROR: Attempting to commit sensitive files!"
    echo "Please remove them from staging:"
    echo "  git reset HEAD <file>"
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```
