# 📁 Database & File Structure Reference

Quick reference for file locations and the twscrape database.

## Directory Structure

```
ChatRF/
├── modules/
│   └── service_112greece_alerts.py    # The module (Python code)
│
├── data/
│   └── 112greece/                      # Module data directory
│       ├── accounts.db                 # ⚠️ twscrape credentials database
│       └── last_tweet.json             # Last seen tweet tracker
│
└── config/
    └── settings/
        └── config.ini                  # [112Greece] configuration
```

## Important Files

### `accounts.db` ⚠️ CRITICAL

**Location:** `data/112greece/accounts.db`

**Purpose:** Contains encrypted Twitter account credentials managed by twscrape

**Created by:** Running `twscrape add_accounts` from the `data/112greece/` directory

**Security:**
- Contains sensitive credentials (encrypted)
- Include in backups
- Add to `.gitignore` if using version control
- Don't share publicly

**How to create:**
```bash
cd /path/to/ChatRF/data/112greece
# Create an account.txt file containing your credentials in the format username:password:email:email_password
# Then, run the command:
twscrape add_accounts ./account.txt username:password:email:email_password
twscrape login_accounts
```

**If missing:**
The module will fail to check Twitter. You'll see errors like:
```
Error checking for tweets: No accounts available
```

**Solution:** Re-run twscrape setup from the correct directory.

### `last_tweet.json`

**Location:** `data/112greece/last_tweet.json`

**Purpose:** Tracks the last seen tweet ID to avoid duplicate announcements

**Created by:** Module automatically on first successful tweet check

**Contents:**
```json
{
  "last_tweet_id": 1234567890123456789,
  "last_updated": "2026-02-03T12:34:56.789Z"
}
```

**If missing:** Module will announce the most recent tweet on first run (if it matches filters)

**To reset:** Delete this file to re-announce the latest tweet

## Setup Checklist

- [ ] Module installed: `modules/service_112greece_alerts.py`
- [ ] Data directory exists: `data/112greece/`
- [ ] twscrape database created: `data/112greece/accounts.db`
- [ ] Configuration added to: `config/settings/config.ini`
- [ ] Module loaded (check logs)

## Verification Commands

```bash
# Check all required files exist
ls -la modules/service_112greece_alerts.py
ls -la data/112greece/accounts.db
ls -la data/112greece/last_tweet.json  # May not exist until first check
grep -A5 "\[112Greece\]" config/settings/config.ini

# Check module loaded
tail -f logs/repeater.log | grep "112 Greece"

# Check twscrape accounts
cd data/112greece
twscrape accounts

# Test tweet fetching
cd data/112greece
python3 -c "from twscrape import API; import asyncio; api = API(); asyncio.run(api.user_tweets(112, limit=1).__anext__())"
```

## Common Issues

### "No accounts available"

**Problem:** `accounts.db` missing or no accounts added

**Solution:**
```bash
cd data/112greece
# Create an account.txt file containing your credentials in the format username:password:email:email_password
# Then, run the command:
twscrape add_accounts ./account.txt username:password:email:email_password
twscrape login_accounts
```

### "accounts.db in wrong location"

**Problem:** Ran `twscrape add_accounts` from wrong directory

**Solution:**
```bash
# Find where it was created
find /path/to/ChatRF -name "accounts.db"

# Move it to correct location
mv /path/to/wronglocation/accounts.db data/112greece/

# Or just recreate it in the right place
cd data/112greece
# Create an account.txt file containing your credentials in the format username:password:email:email_password
# Then, run the command:
twscrape add_accounts ./account.txt username:password:email:email_password
```

### "Module can't find database"

**Problem:** Module looking in wrong directory

**Check logs for:**
```
twscrape database location: data/112greece/accounts.db
```

**Verify:**
```bash
ls -la data/112greece/accounts.db
```

## Backup Recommendations

### What to backup:

1. **accounts.db** - Your Twitter credentials
2. **last_tweet.json** - Tweet tracking state
3. **config.ini** - Your configuration

### Backup script:

```bash
#!/bin/bash
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp data/112greece/accounts.db "$BACKUP_DIR/"
cp data/112greece/last_tweet.json "$BACKUP_DIR/"
cp config/settings/config.ini "$BACKUP_DIR/"

echo "Backup created in $BACKUP_DIR"
```

### Restore:

```bash
# Restore from backup
cp backup_YYYYMMDD_HHMMSS/accounts.db data/112greece/
cp backup_YYYYMMDD_HHMMSS/last_tweet.json data/112greece/
cp backup_YYYYMMDD_HHMMSS/config.ini config/settings/
```

## Migration to New Server

Moving ChatRF to a new machine:

### Option 1: Copy database
```bash
# On old server
tar -czf 112greece_backup.tar.gz data/112greece/

# Transfer to new server
scp 112greece_backup.tar.gz user@newserver:/path/to/ChatRF/

# On new server
cd /path/to/ChatRF
tar -xzf 112greece_backup.tar.gz
```

### Option 2: Re-add accounts
```bash
# On new server
cd data/112greece
# Create an account.txt file containing your credentials in the format username:password:email:email_password
# Then, run the command:
twscrape add_accounts ./account.txt username:password:email:email_password
twscrape login_accounts
```

## Security Notes

- **Never commit** `accounts.db` to version control
- **Always add** to `.gitignore`:
  ```gitignore
  data/112greece/accounts.db
  ```
- **Keep secure** - contains Twitter credentials
- **Backup encrypted** if storing in cloud
- **Rotate passwords** periodically

## Quick Commands Reference

```bash
# Check if database exists
[ -f data/112greece/accounts.db ] && echo "✅ Database found" || echo "❌ Database missing"

# Check database size
ls -lh data/112greece/accounts.db

# View last seen tweet
cat data/112greece/last_tweet.json | python3 -m json.tool

# Reset (re-announce latest)
rm data/112greece/last_tweet.json

# View twscrape accounts
cd data/112greece && twscrape accounts

# Test login
cd data/112greece && twscrape login_accounts
```

---

**Questions?** See [README.md](README.md) or [SECURITY.md](SECURITY.md)

73! 📡
