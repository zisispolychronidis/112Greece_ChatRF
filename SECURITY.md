# 🔐 Security Guide: Setting Up twscrape Safely

## Understanding Email Password Requirement

### What is "email password"?

When twscrape asks for `EMAIL_PASSWORD`, it means:
- The password for the **email account** linked to your Twitter account
- **NOT** your Twitter password
- **NOT** your main email password (use app-specific instead!)

### Why does twscrape need it?

Twitter often requires email verification when logging in, especially for:
- New login locations
- Bot/automation accounts
- Security checks
- Suspicious activity detection

twscrape needs email access to:
- Retrieve verification codes
- Confirm login attempts
- Pass Twitter's automated detection

## 🛡️ Secure Setup Methods

### Method 1: Dedicated Accounts (RECOMMENDED) ⭐

**Best practice for security and peace of mind:**

1. **Create a new email account** just for this bot
   - Gmail: https://accounts.google.com/signup
   - Outlook: https://outlook.live.com/owa/
   - Example: `my112scraper@gmail.com`

2. **Create a new Twitter account** using that email
   - Twitter: https://twitter.com/i/flow/signup
   - Example username: `@my112alerts`

3. **Generate app-specific password** for the email
   - See instructions below

4. **Use these credentials** in twscrape

**Benefits:**
- ✅ Zero risk to personal accounts
- ✅ Easy to revoke/delete if compromised
- ✅ Clean separation of concerns
- ✅ No impact if account gets suspended
- ✅ Simple password management

**Example credentials:**
```
Twitter username: my112alerts
Twitter password: BotPassword123!
Email: my112scraper@gmail.com
Email app password: abcd efgh ijkl mnop (16 chars from Google)
```

### Method 2: App-Specific Passwords

If you want to use an existing account, **NEVER use your main email password**. Instead, create an app-specific password:

#### Gmail (Google Account)

1. **Enable 2-Factor Authentication** (required)
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification" → Turn on

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and device type
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

3. **Use this password** instead of your regular Gmail password

#### Outlook/Hotmail (Microsoft Account)

1. **Enable 2-Step Verification**
   - Go to: https://account.microsoft.com/security
   - Click "Advanced security options"
   - Turn on "Two-step verification"

2. **Create App Password**
   - Under "App passwords", click "Create a new app password"
   - Copy the generated password

3. **Use this password** for twscrape

#### Yahoo Mail

1. **Go to Account Security**
   - https://login.yahoo.com/account/security
   
2. **Generate App Password**
   - Click "Generate app password"
   - Select "Other App"
   - Name it "twscrape" or "112 Bot"
   - Copy the password

3. **Use this password** for twscrape

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T:
- Use your main email password (use app-specific!)
- Use your personal Twitter account for bots
- Share credentials or commit them to git
- Reuse passwords across services
- Use simple passwords like "password123"

### ✅ DO:
- Create dedicated bot accounts
- Use app-specific passwords
- Use strong, unique passwords
- Store credentials securely (password manager)
- Keep email and Twitter passwords different

## 🔒 Password Security Best Practices

1. **Use a Password Manager**
   - Bitwarden (free, open-source)
   - 1Password
   - LastPass
   - KeePass

2. **Strong Password Format**
   ```
   Good: My112Bot!2024$Secure
   Bad:  password123
   ```

3. **Unique Passwords**
   - Never reuse passwords
   - Use different password for Twitter and email
   - Change passwords if compromised

4. **Store Safely**
   - Use password manager
   - Don't write in plain text files
   - Don't commit to version control
   - Don't share in screenshots/messages
   - The `accounts.db` file contains encrypted credentials - keep it secure!

## 🗄️ Database File Security

The twscrape database (`data/112greece/accounts.db`) contains your Twitter credentials:

- **Location:** `ChatRF/data/112greece/accounts.db`
- **Contents:** Encrypted Twitter account credentials
- **Backup:** Include in your ChatRF backups
- **Permissions:** Keep secure, don't share publicly
- **Version Control:** Add `data/112greece/accounts.db` to `.gitignore`

**If moving ChatRF to a new machine:**
1. Copy the entire `data/112greece/` directory
2. Or re-run `twscrape add_accounts` on the new machine

## 🚨 What If Credentials Are Compromised?

If you think your credentials are exposed:

### For Dedicated Accounts:
1. Delete the Twitter account
2. Delete the email account
3. Create new ones
4. Update twscrape

### For Personal Accounts:
1. **Immediately** revoke app-specific password
2. Change your Twitter password
3. Change your email password
4. Review account activity
5. Enable alerts for suspicious logins

## 📋 Setup Checklist

Use this checklist to set up securely:

- [ ] Decide: Dedicated accounts or app-specific passwords?
- [ ] If dedicated: Create new email account
- [ ] If dedicated: Create new Twitter account linked to new email
- [ ] Generate app-specific password for email
- [ ] Test login with credentials manually
- [ ] Add credentials to twscrape
- [ ] Run `twscrape login_accounts`
- [ ] Verify login successful
- [ ] Store credentials in password manager
- [ ] Delete credentials from shell history (`history -c`)

## 🔍 Troubleshooting

### "Login failed" or "Invalid credentials"

**Check:**
- ✓ Using **email password**, not Twitter password?
- ✓ Using **app-specific password**, not main email password?
- ✓ Twitter account uses the email you specified?
- ✓ 2FA enabled on email (required for app passwords)?
- ✓ Password copied correctly (no extra spaces)?

### "Email verification required"

This is why twscrape needs email access! Make sure:
- Email password is correct
- App-specific password is generated
- Twitter account uses this email

### "Account locked" or "Suspicious activity"

- Twitter may flag bot activity
- Use dedicated accounts (harder to flag)
- Don't scrape too aggressively
- Respect rate limits

## 📚 Additional Resources

- **Google App Passwords Guide:** https://support.google.com/accounts/answer/185833
- **Microsoft App Passwords:** https://support.microsoft.com/account-billing/manage-app-passwords
- **Twitter Automation Rules:** https://help.twitter.com/en/rules-and-policies/twitter-automation
- **twscrape Documentation:** https://github.com/vladkens/twscrape

## 💡 Final Recommendations

**For 112 Greece Alerts Module:**

1. **Create a fresh Gmail account**
   - Example: `greece112alerts@gmail.com`

2. **Create a fresh Twitter account**
   - Example: `@112AlertBot`
   - Bio: "Automated bot for monitoring 112 Greece alerts"

3. **Enable 2FA on Gmail**

4. **Generate app password**

5. **Navigate to data directory and add to twscrape:**
   ```bash
   cd /path/to/ChatRF/data/112greece

   # Create an account.txt file containing your credentials in the format username:password:email:email_password
   # Then, run the command:
   twscrape add_accounts ./account.txt username:password:email:email_password
   twscrape login_accounts
   ```

6. **Verify database created:**
   ```bash
   ls -la accounts.db
   # Should see: accounts.db with your credentials
   ```

7. **Lock down the accounts:**
   - Don't use for anything else
   - Monitor for unusual activity
   - Rotate passwords periodically
   - Back up `data/112greece/` directory
   - Add `accounts.db` to `.gitignore` if using git

This gives you maximum security with minimal risk! 🛡️

---

**Questions?** See README.md or ask in ChatRF discussions.

Stay secure! 🔐