# 🔐 Secure Setup Guide for Tejas AI

## ⚠️ **IMPORTANT SECURITY NOTICE**

**Never commit your real Google OAuth credentials or MongoDB passwords to Git!** This guide will show you how to set up the project securely.

## 🚀 **Quick Setup Steps**

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/TejasAi.git
cd TejasAi
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure Credentials (SECURE WAY)**

#### **Option A: Using Template (Recommended)**
```bash
# Copy the template file
cp config_template.py config.py

# Edit config.py with your real credentials
# NEVER commit this file to git!
```

#### **Option B: Using Environment Variables (Most Secure)**
Create a `.env` file (this will be automatically ignored by git):
```bash
# .env file
GOOGLE_CLIENT_ID=your_actual_client_id
GOOGLE_CLIENT_SECRET=your_actual_client_secret
MONGODB_URI=mongodb://username:password@localhost:27017/
```

### 4. **Set Up Google OAuth**

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project or select existing one**
3. **Enable APIs:**
   - Google+ API
   - Google OAuth2 API
4. **Create OAuth 2.0 credentials:**
   - Application type: Desktop application
   - Add redirect URI: `http://localhost:8080/callback`
5. **Copy your credentials to config.py**

### 5. **Set Up MongoDB**

#### **Local MongoDB:**
```bash
# Install MongoDB locally
# Start MongoDB service
# Use default connection: mongodb://localhost:27017/
```

#### **MongoDB Atlas (Cloud):**
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Add to config.py

### 6. **Run the Application**
```bash
python main.py
```

## 🔒 **Security Best Practices**

### **Files to NEVER Commit:**
- ✅ `config.py` (with real credentials)
- ✅ `.env` files
- ✅ `user_data.json`
- ✅ `user_token.json`
- ✅ `auth_tokens.json`
- ✅ `ui_settings.json`
- ✅ `reminders.json`

### **Files Safe to Commit:**
- ✅ `config_template.py`
- ✅ `requirements.txt`
- ✅ Source code files
- ✅ Documentation

## 🛡️ **Verification Checklist**

Before pushing to GitHub, ensure:

- [ ] `config.py` is in `.gitignore`
- [ ] `.env` files are in `.gitignore`
- [ ] No real credentials in any committed files
- [ ] `config_template.py` exists for other users
- [ ] Sensitive JSON files are ignored
- [ ] Voice models are ignored (large files)

## 🚨 **If You Accidentally Committed Credentials**

### **Immediate Actions:**
1. **Revoke the credentials immediately** in Google Cloud Console
2. **Generate new credentials**
3. **Remove the file from git history:**
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config.py" \
  --prune-empty --tag-name-filter cat -- --all
```

### **Force Push (Use with caution):**
```bash
git push origin --force
```

## 📋 **Environment Variables Reference**

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID | `123456789-abc123.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Client Secret | `GOCSPX-abc123def456` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `DEBUG_MODE` | Enable debug logging | `True` or `False` |

## 🆘 **Troubleshooting**

### **Common Issues:**
- **"Invalid credentials"**: Check Google OAuth setup
- **"MongoDB connection failed"**: Verify MongoDB service and connection string
- **"Redirect URI mismatch"**: Ensure callback URL matches exactly

### **Need Help?**
- Check the [main README.md](README.md)
- Open an issue on GitHub
- Review Google OAuth documentation

---

**Remember: Security first! Never share your credentials publicly.**
