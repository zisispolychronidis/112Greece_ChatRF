# 🚨 112 Greece Alerts Module - Quick Start Guide

## What You're Getting

A complete ChatRF module that monitors @112Greece for emergency alerts and announces them over your repeater!

## 📦 Files Included

1. **service_112greece_alerts.py** - The main module (place in `modules/`)
2. **config_snippet.ini** - Configuration to add to your `config.ini`
3. **install.sh** - Automated installation script
4. **test_parsing.py** - Test script to see how tweets are parsed
5. **README.md** - Complete documentation

## ⚡ Quick Installation

### Windows Prerequisites

**Step 1:** Install Git for Windows
- Download: https://git-scm.com/download/win
- Install with default options
- This includes **Git Bash**

**Step 2:** Open Git Bash
- Right-click in the folder containing `install.sh`
- Select **"Git Bash Here"**

### Option 1: Automated (Recommended)

```bash
# 1. Run the installation script and follow the instructions
./install.sh /path/to/ChatRF

# 2. Restart ChatRF
```

#### 🔐 About Email Password (twscrape)

**What is it?** The password for the email account linked to your Twitter account.

**⚠️ Use App-Specific Passwords (NOT your main email password):**

- **Gmail:** https://myaccount.google.com/apppasswords (requires 2FA enabled)
- **Outlook:** Account Security → App passwords
- **Yahoo:** Account Security → Generate app password

**🛡️ Best Practice:** Create a dedicated email + Twitter account just for scraping:
```
Email: my112bot@gmail.com
Twitter: @my112scraper
Format: my112scraper:twitterpass:my112bot@gmail.com:gmail-app-password
```

This keeps your personal accounts safe and secure!

### Option 2: Manual

```bash
# 1. Install dependency
pip install twscrape

# 2. Copy module
cp service_112greece_alerts.py /path/to/ChatRF/modules/

# 3. Create data directory and set up Twitter
mkdir -p /path/to/ChatRF/data/112greece
cd /path/to/ChatRF/data/112greece

# Create an account.txt file that contains your credentials

# Register credentials (IMPORTANT: Read email password note above!)
twscrape add_accounts ./account.txt username:password:email:email_password
twscrape login_accounts

# This creates accounts.db in the correct location

# 4. Add this to config/settings/config.ini:
[112Greece]
check_interval = 300
announcement_prefix = Προσοχή! Νέα ειδοποίηση από το 112
filter_regions = 

# 5. Restart ChatRF
```

**📁 Database Location:**
The module expects twscrape's database at: `data/112greece/accounts.db`

**⚠️ Email Password Security:**
- Use **app-specific passwords**, not your main email password
- Best practice: Create dedicated email + Twitter accounts for scraping
- See detailed explanation in the automated option above

## ✅ Verify It's Working

```bash
# Check logs
tail -f logs/repeater.log | grep "112 Greece"

# You should see:
# [INFO] Initializing 112 Greece Alerts module
# [INFO] twscrape database location: data/112greece/accounts.db
# [INFO] 112 Greece Alerts service started (checking every 300s)
```

**Check required files exist:**
```bash
# Twitter credentials database
ls -la data/112greece/accounts.db

# Module file
ls -la modules/service_112greece_alerts.py

# After first check, last tweet tracker
ls -la data/112greece/last_tweet.json
```

## 🎯 Configuration Examples

### Announce All Alerts
```ini
[112Greece]
check_interval = 300
announcement_prefix = Προσοχή! Νέα ειδοποίηση από το 112
filter_regions = 
```

### Only Your Region (e.g., North Aegean)
```ini
[112Greece]
check_interval = 300
announcement_prefix = Προσοχή! Νέα ειδοποίηση από το 112
filter_regions = Βορείου_Αιγαίου
```

### Multiple Regions
```ini
[112Greece]
check_interval = 300
announcement_prefix = Προσοχή! Νέα ειδοποίηση από το 112
filter_regions = Βορείου_Αιγαίου,Κεντρική_Μακεδονία,Αττική
```

### English Announcements
```ini
[112Greece]
check_interval = 300
announcement_prefix = Emergency alert from 112 Greece
filter_regions = 
```

## 🧪 Testing

Run the test script to see how tweets are parsed:

```bash
python3 test_parsing.py
```

This shows you what would be announced for various tweet formats!

## 📝 How Announcements Work

**Example Tweet:**
```
⚠️ Ενεργοποίηση 1️⃣1️⃣2️⃣ 
🆘 Λόγω έντονων καιρικών φαινομένων που αναμένονται 
στην Περιφέρεια #Βορείου_Αιγαίου προσοχή στις 
μετακινήσεις σας από σήμερα το μεσημέρι 01-02-2026 
έως αύριο το πρωί 02-02-2026. 
```

**What Gets Announced:**
```
Προσοχή! Νέα ειδοποίηση από το 112 για την περιοχή 
Βορείου Αιγαίου. από 01-02-2026 έως 02-02-2026. 
Λόγω έντονων καιρικών φαινομένων που αναμένονται 
στην Περιφέρεια προσοχή στις μετακινήσεις σας...
```

The module:
- ✅ Extracts the region from hashtag
- ✅ Extracts the time period
- ✅ Removes emojis, URLs, and @mentions
- ✅ Creates clean, speakable text

## 🔍 Common Regions

Find your region hashtag from @112Greece tweets:

- `Βορείου_Αιγαίου` - North Aegean
- `Κεντρική_Μακεδονία` - Central Macedonia
- `Αττική` - Attica (Athens area)
- `Θεσσαλονίκη` - Thessaloniki
- `Κρήτη` - Crete
- `Πελοπόννησος` - Peloponnese
- `Ιόνια_Νησιά` - Ionian Islands
- `Στερεά_Ελλάδα` - Central Greece
- And many more...

**Note:** Use the exact text from the hashtag, including underscores!

## 🐛 Troubleshooting

### "twscrape not installed"
```bash
pip install twscrape
```

### "No Twitter account configured"
```bash
twscrape add_accounts ./account.txt username:password:email:email_password
twscrape login_accounts
```

### Not announcing alerts
- Check if tweets match your region filter
- Verify only "activation" alerts (⚠️) are announced
- Check logs: `grep "112 Greece" logs/repeater.log`

### Module not loading
- Ensure file is in `modules/` directory
- Check for syntax errors: `python3 -m py_compile service_112greece_alerts.py`
- Review logs: `tail -f logs/repeater_errors.log`

## 💡 Tips

1. **Check Interval:** Don't set too low (recommended: 300-600 seconds) to avoid rate limiting
2. **Region Filtering:** Leave empty to get all alerts, or specify your specific region
3. **Testing:** Delete `data/112greece_last_tweet.json` to re-announce the latest tweet
4. **Twitter Account:** Consider creating a dedicated account just for scraping

## 📚 More Information

See **README.md** for complete documentation including:
- Detailed configuration options
- Advanced customization
- API reference
- Troubleshooting guide

## 🆘 Need Help?

- Check the complete README.md
- Review ChatRF documentation on adding modules
- Test with test_parsing.py to verify parsing
- Check logs for error messages

---

**73 de SV2TMT** 🎙️📡

Stay safe! 🚨
