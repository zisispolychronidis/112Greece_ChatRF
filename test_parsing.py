#!/usr/bin/env python3
"""
Test script for 112 Greece Alerts Module
Demonstrates how tweets are parsed and what would be announced
"""

import re

def parse_alert(tweet_text):
    """Parse a 112 Greece alert tweet"""
    result = {
        'full_text': tweet_text,
        'region': None,
        'date_range': None,
        'is_activation': False
    }
    
    # Check if this is an activation alert
    if '⚠️' in tweet_text or 'Ενεργοποίηση' in tweet_text:
        result['is_activation'] = True
    
    # Extract region using hashtag pattern
    region_match = re.search(r'#(\w+(?:_\w+)*)', tweet_text)
    if region_match:
        result['region'] = region_match.group(1)
    
    # Extract date range
    date_pattern = r'από.*?(\d{2}-\d{2}-\d{4}).*?έως.*?(\d{2}-\d{2}-\d{4})'
    date_match = re.search(date_pattern, tweet_text)
    if date_match:
        result['date_range'] = f"από {date_match.group(1)} έως {date_match.group(2)}"
    
    return result


def create_announcement(parsed_alert, prefix="Προσοχή! Νέα ειδοποίηση από το 112"):
    """Create announcement text from parsed alert"""
    announcement = prefix
    
    if parsed_alert['region']:
        region = parsed_alert['region'].replace('_', ' ')
        announcement += f" για την περιοχή {region}."
    else:
        announcement += "."
    
    if parsed_alert['date_range']:
        announcement += f" {parsed_alert['date_range']}."
    
    # Clean text
    clean_text = re.sub(r'[⚠️🆘‼️ℹ️1️⃣2️⃣]', '', parsed_alert['full_text'])
    clean_text = re.sub(r'https?://\S+', '', clean_text)
    clean_text = re.sub(r'@\w+', '', clean_text)
    clean_text = re.sub(r'#\w+', '', clean_text)
    clean_text = ' '.join(clean_text.split())
    
    announcement += f" {clean_text}"
    
    return announcement


# Example tweets
examples = [
    {
        'name': 'Severe Weather Alert',
        'text': '''⚠️ Ενεργοποίηση 1️⃣1️⃣2️⃣ 
🆘 Λόγω έντονων καιρικών φαινομένων που αναμένονται στην Περιφέρεια #Βορείου_Αιγαίου προσοχή στις μετακινήσεις σας από σήμερα το μεσημέρι 01-02-2026 έως αύριο το πρωί 02-02-2026. 
‼️ Ακολουθείτε τις οδηγίες των Αρχών. 
ℹ️ https://bit.ly/3YwYXZP  

@pyrosvestiki  
@hellenicpolice'''
    },
    {
        'name': 'Fire Alert',
        'text': '''⚠️ Ενεργοποίηση 1️⃣1️⃣2️⃣ 
🆘 Πυρκαγιά στην περιοχή #Αττική. Απομακρυνθείτε από την περιοχή. 
‼️ Ακολουθείτε τις οδηγίες των Αρχών.
ℹ️ https://bit.ly/example

@pyrosvestiki'''
    },
    {
        'name': 'Multi-region Alert',
        'text': '''⚠️ Ενεργοποίηση 1️⃣1️⃣2️⃣ 
🆘 Λόγω ισχυρών ανέμων στις περιοχές #Κεντρική_Μακεδονία και #Θεσσαλία από 03-02-2026 έως 04-02-2026.
‼️ Προσοχή στις μετακινήσεις.'''
    }
]

print("=" * 80)
print("112 GREECE ALERTS - PARSING TEST")
print("=" * 80)
print()

for example in examples:
    print("-" * 80)
    print(f"EXAMPLE: {example['name']}")
    print("-" * 80)
    print()
    print("ORIGINAL TWEET:")
    print(example['text'])
    print()
    
    parsed = parse_alert(example['text'])
    
    print("PARSED DATA:")
    print(f"  Is Activation: {parsed['is_activation']}")
    print(f"  Region: {parsed['region']}")
    print(f"  Date Range: {parsed['date_range']}")
    print()
    
    announcement = create_announcement(parsed)
    print("ANNOUNCEMENT (TTS):")
    print(f"  {announcement}")
    print()
    print()

print("=" * 80)
print()

# Test region filtering
print("REGION FILTERING EXAMPLES:")
print("-" * 80)
print()

filter_regions = {'Βορείου_Αιγαίου', 'Αττική'}
print(f"Active Filters: {filter_regions}")
print()

for example in examples:
    parsed = parse_alert(example['text'])
    would_announce = parsed['region'] in filter_regions if parsed['region'] else False
    status = "✅ WOULD ANNOUNCE" if would_announce else "❌ WOULD SKIP"
    print(f"{status}: {example['name']} (Region: {parsed['region']})")

print()
print("=" * 80)
