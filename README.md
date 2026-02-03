# 🚨 112 Greece Emergency Alerts Module

This module monitors the [@112Greece](https://twitter.com/112Greece) Twitter account for emergency alerts and automatically announces them over your ChatRF repeater.

**This module was written with Claude, don't expect high-quality code.**

## 📋 Overview

The 112 service in Greece sends emergency alerts for severe weather, natural disasters, and other emergencies. This module:

- ✅ Continuously monitors @112Greece for new tweets
- ✅ Parses alert messages to extract key information (region, time period, etc.)
- ✅ Filters alerts by region (optional)
- ✅ Announces new alerts over the repeater using text-to-speech
- ✅ Tracks seen tweets to avoid duplicate announcements
- ✅ Persists state across restarts

## 🔧 Installation

Check the [QuickStart Documentation](https://github.com/zisispolychronidis/112Greece_ChatRF/blob/main/QUICKSTART.md) for installation instructions.

## ⚙️ Configuration Options

### `check_interval`
How often to check for new tweets (in seconds).
- **Default:** 300 (5 minutes)
- **Recommended:** 300-600 (don't set too low to avoid rate limiting)

### `announcement_prefix`
Text spoken before each alert announcement.
- **Default:** "Προσοχή! Νέα ειδοποίηση από το 112"
- **Examples:**
  - "Προσοχή! Νέα ειδοποίηση από το 112"
  - "Emergency alert from 112 Greece"
  - "Νέα έκτακτη ανακοίνωση"

### `filter_regions`
Comma-separated list of regions to monitor. Leave empty to announce all alerts.
- **Default:** Empty (all alerts)
- **Format:** Use hashtag text from tweets with underscores
- **Examples:**
  ```ini
  # Only announce alerts for North Aegean
  filter_regions = Βορείου_Αιγαίου
  
  # Multiple regions
  filter_regions = Βορείου_Αιγαίου,Κεντρική_Μακεδονία,Αττική
  ```

**Common regions from @112Greece:**
- `Βορείου_Αιγαίου` (North Aegean)
- `Κεντρική_Μακεδονία` (Central Macedonia)
- `Αττική` (Attica)
- `Θεσσαλονίκη` (Thessaloniki)
- `Κρήτη` (Crete)
- And many more...

## 📝 How It Works

### File Structure

The module creates and uses the following files:

```
ChatRF/
├── modules/
│   └── service_112greece_alerts.py  # The module
└── data/
    └── 112greece/
        ├── accounts.db              # twscrape database (Twitter credentials)
        └── last_tweet.json          # Last seen tweet tracking
```

**Important files:**
- `accounts.db` - Contains encrypted Twitter account credentials (managed by twscrape)
- `last_tweet.json` - Tracks the last seen tweet ID to avoid duplicates

### Tweet Parsing

The module recognizes the standard 112 Greece tweet format:

```
⚠️ Ενεργοποίηση 1️⃣1️⃣2️⃣ 
🆘 Λόγω έντονων καιρικών φαινομένων που αναμένονται στην Περιφέρεια #Βορείου_Αιγαίου 
προσοχή στις μετακινήσεις σας από σήμερα το μεσημέρι 01-02-2026 έως αύριο το πρωί 02-02-2026. 
‼️ Ακολουθείτε τις οδηγίες των Αρχών. 
ℹ️ https://bit.ly/3YwYXZP
```

It extracts:
- **Region** from hashtag (#Βορείου_Αιγαίου)
- **Time period** (από... έως...)
- **Main message** (cleaned of emojis and links)

### Announcement Format

Example announcement in Greek:

> "Προσοχή! Νέα ειδοποίηση από το 112 για την περιοχή Βορείου Αιγαίου. από 01-02-2026 έως 02-02-2026. Λόγω έντονων καιρικών φαινομένων που αναμένονται στην Περιφέρεια προσοχή στις μετακινήσεις σας από σήμερα το μεσημέρι έως αύριο το πρωί. Ακολουθείτε τις οδηγίες των Αρχών."

### State Persistence

The module saves the last seen tweet ID to `data/112greece_last_tweet.json`. This ensures:
- No duplicate announcements after restarts
- Only new alerts are announced
- Reliable tracking even if the module is temporarily disabled

## 🧪 Testing

### Test the Module

You can test if the module is working by checking the logs:

```bash
tail -f logs/repeater.log | grep "112 Greece"
```

You should see:
```
[INFO] Initializing 112 Greece Alerts module
[INFO] 112 Greece Alerts service started (checking every 300s)
[DEBUG] Fetching latest tweets from @112Greece
```

### Verify Tweet Detection

To verify the module can detect tweets:

1. Check the state file:
```bash
cat data/112greece_last_tweet.json
```

2. Temporarily lower the check interval for testing:
```ini
check_interval = 60  # Check every minute
```

3. Monitor the logs for new tweet detection

### Trigger a Manual Test

You can force an announcement by temporarily deleting the state file:

```bash
rm data/112greece_last_tweet.json
```

The next check cycle will treat the latest tweet as "new" and announce it (if it matches your filters).

## 🐛 Troubleshooting

### Module Not Loading

**Check the logs:**
```bash
grep "112 Greece" logs/repeater.log
```

**Common issues:**
- twscrape not installed: `pip install twscrape`
- No Twitter account configured in twscrape
- Module file not in `modules/` directory

### No Announcements

**Possible causes:**

1. **No new tweets** - @112Greece hasn't posted recently
2. **Region filtering** - Tweet region doesn't match your filter
3. **Not activation alerts** - Only tweets with ⚠️ or "Ενεργοποίηση" are announced
4. **Already seen** - Tweet was posted before module started
5. **twscrape database not found** - accounts.db not in correct location

**Debug steps:**
```bash
# Check last seen tweet
cat data/112greece/last_tweet.json

# Check if twscrape database exists
ls -la data/112greece/accounts.db

# If accounts.db is missing, set up twscrape again:
cd data/112greece
twscrape add_accounts USERNAME PASSWORD EMAIL EMAIL_PASSWORD
twscrape login_accounts

# Enable debug logging in config.ini
[Logging]
level = DEBUG

# Watch for tweet detection
tail -f logs/repeater.log | grep -A 5 "New tweet"
```

### Twitter Rate Limiting

If you see rate limit errors:
- Increase `check_interval` (recommended: 300-600 seconds)
- Ensure you have valid Twitter credentials in twscrape
- Check if your Twitter account is rate limited

## 🔒 Security Considerations

- **Twitter Credentials:** Store credentials securely, consider using a dedicated account
- **Data Directory:** The `data/` directory contains state files - back up if needed
- **Network Access:** Module requires internet access to fetch tweets

## 📊 Advanced Usage

### Custom Announcement Logic

You can modify the `_should_announce()` method to add custom filtering:

```python
def _should_announce(self, parsed_alert: dict) -> bool:
    # Only announce during certain hours
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 6 or hour > 22:  # Silent hours
        return False
    
    # Original logic
    return super()._should_announce(parsed_alert)
```

### Integration with Other Modules

The module sets `self.repeater.latest_112_alert` with the last alert, which other modules can access:

```python
# In another module
if hasattr(self.repeater, 'latest_112_alert'):
    alert = self.repeater.latest_112_alert
    # Do something with alert data
```

## 📄 License

This module is part of ChatRF and follows the same license.

## 🤝 Contributing

Found a bug or want to improve the module? Contributions are welcome!

- Report issues on GitHub
- Submit pull requests with improvements
- Share your customizations with the community

## 📞 Support

For help with this module:
1. Check the troubleshooting section above
2. Review ChatRF logs: `logs/repeater.log`
3. Ask in ChatRF GitHub Discussions
4. Check @112Greece Twitter for alert format changes

## 🎓 Credits

- Built for ChatRF by Claude
- Uses [twscrape](https://github.com/vladkens/twscrape) for Twitter scraping
- Monitors [@112Greece](https://twitter.com/112Greece) official emergency account

---

**73 de SV2TMT** 🎙️📡

Stay safe and informed! 🚨
