"""
112 Greece Emergency Alerts Module

Monitors @112Greece Twitter account for emergency alerts and announces them over the repeater.

Dependencies:
    pip install twscrape

Configuration (add to config.ini):
    [112Greece]
    check_interval = 300  # Check every 5 minutes (in seconds)
    announcement_prefix = Emergency alert from 112 Greece
    # Optional: Filter by regions (comma-separated, leave empty for all)
    filter_regions = Βορείου_Αιγαίου,Κεντρική_Μακεδονία
"""

from modules.base import BackgroundServiceModule
import time
import re
from datetime import datetime, timezone
from typing import Optional, Set
import asyncio
from pathlib import Path
import json


class Greece112AlertsModule(BackgroundServiceModule):
    # Metadata
    name = "112 Greece Alerts"
    version = "1.0.0"
    description = "Monitors @112Greece for emergency alerts"
    
    def initialize(self):
        """Initialize the module and load configuration"""
        self.logger.info("Initializing 112 Greece Alerts module")
        
        # Load configuration
        self.check_interval = self.config.config.getint(
            '112Greece', 'check_interval', fallback=300
        )
        self.announcement_prefix = self.config.config.get(
            '112Greece', 'announcement_prefix', 
            fallback='Προσοχή! Νέα ειδοποίηση από το 112'
        )
        
        # Optional region filtering
        filter_regions_str = self.config.config.get(
            '112Greece', 'filter_regions', fallback=''
        )
        if filter_regions_str.strip():
            self.filter_regions = set(
                r.strip() for r in filter_regions_str.split(',')
            )
            self.logger.info(f"Filtering alerts for regions: {self.filter_regions}")
        else:
            self.filter_regions = None
            self.logger.info("No region filtering - announcing all alerts")
        
        # Set up data directory for persistent files
        self.data_dir = Path("data/112greece")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # State file to track last seen tweet
        self.state_file = self.data_dir / "last_tweet.json"
        
        # Load last seen tweet ID
        self.last_tweet_id: Optional[int] = self._load_last_tweet_id()
        
        # Check if twscrape is installed
        try:
            import twscrape
            self.twscrape = twscrape
            self.logger.info("twscrape library loaded successfully")
        except ImportError:
            self.logger.error("twscrape not installed! Run: pip install twscrape")
            self.logger.error("Module will be disabled")
            self.enabled = False
            return
        
        # Configure twscrape database path
        # twscrape uses accounts.db in its working directory by default
        # We'll set it to use our data directory
        self.db_path = self.data_dir / "accounts.db"
        self.logger.info(f"twscrape database location: {self.db_path}")
        
        # Seen tweet IDs to avoid duplicates in same session
        self.seen_tweets: Set[int] = set()
        if self.last_tweet_id:
            self.seen_tweets.add(self.last_tweet_id)
    
    def _load_last_tweet_id(self) -> Optional[int]:
        """Load the last seen tweet ID from state file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    tweet_id = data.get('last_tweet_id')
                    if tweet_id:
                        self.logger.info(f"Loaded last tweet ID: {tweet_id}")
                        return int(tweet_id)
        except Exception as e:
            self.logger.error(f"Error loading state file: {e}")
        return None
    
    def _save_last_tweet_id(self, tweet_id: int):
        """Save the last seen tweet ID to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_tweet_id': tweet_id,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }, f)
            self.logger.debug(f"Saved last tweet ID: {tweet_id}")
        except Exception as e:
            self.logger.error(f"Error saving state file: {e}")
    
    def _parse_alert(self, tweet_text: str) -> dict:
        """
        Parse a 112 Greece alert tweet and extract key information
        
        Returns dict with:
            - full_text: Complete tweet text
            - region: Affected region (if found)
            - date_range: Time period of alert (if found)
            - is_activation: Whether this is an activation alert
        """
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
        # Example: #Βορείου_Αιγαίου
        region_match = re.search(r'#(\w+(?:_\w+)*)', tweet_text)
        if region_match:
            result['region'] = region_match.group(1)
        
        # Extract date range
        # Pattern: "από [date] έως [date]" or similar
        date_pattern = r'από.*?(\d{2}-\d{2}-\d{4}).*?έως.*?(\d{2}-\d{2}-\d{4})'
        date_match = re.search(date_pattern, tweet_text)
        if date_match:
            result['date_range'] = f"από {date_match.group(1)} έως {date_match.group(2)}"
        
        return result
    
    def _should_announce(self, parsed_alert: dict) -> bool:
        """Determine if an alert should be announced based on filters"""
        
        # If no region filtering, announce all activation alerts
        if not self.filter_regions:
            return parsed_alert['is_activation']
        
        # If region filtering is enabled, check if alert region matches
        if parsed_alert['region']:
            should_announce = parsed_alert['region'] in self.filter_regions
            if should_announce:
                self.logger.info(
                    f"Alert matches filter region: {parsed_alert['region']}"
                )
            else:
                self.logger.debug(
                    f"Alert region {parsed_alert['region']} not in filter"
                )
            return should_announce and parsed_alert['is_activation']
        
        # No region found but we have filters - don't announce
        self.logger.debug("No region found in alert, skipping")
        return False
    
    def _create_announcement_text(self, parsed_alert: dict) -> str:
        """Create the announcement text from parsed alert"""
        
        # Start with prefix
        announcement = self.announcement_prefix
        
        # Add region if available
        if parsed_alert['region']:
            # Replace underscores with spaces for better speech
            region = parsed_alert['region'].replace('_', ' ')
            announcement += f" για την περιοχή {region}."
        else:
            announcement += "."
        
        # Add date range if available
        if parsed_alert['date_range']:
            announcement += f" {parsed_alert['date_range']}."
        
        # Clean up the full text for speech
        # Remove emojis and special characters
        clean_text = re.sub(r'[⚠️🆘‼️ℹ️1️⃣2️⃣]', '', parsed_alert['full_text'])
        # Remove URLs
        clean_text = re.sub(r'https?://\S+', '', clean_text)
        # Remove @mentions
        clean_text = re.sub(r'@\w+', '', clean_text)
        # Remove hashtags (already extracted region)
        clean_text = re.sub(r'#\w+', '', clean_text)
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        
        # Add the main message
        announcement += f" {clean_text}"
        
        return announcement
    
    async def _check_for_new_tweets(self):
        """Check @112Greece for new tweets (async)"""
        try:
            # Create API instance with our database path
            # Note: twscrape API() looks for accounts.db in current directory by default
            # We need to ensure it uses our data directory
            import os
            original_cwd = os.getcwd()
            
            try:
                # Change to data directory so twscrape finds accounts.db there
                os.chdir(self.data_dir)
                api = self.twscrape.API()
            finally:
                # Always restore original directory
                os.chdir(original_cwd)
            
            # Get user tweets (limit to last 10)
            user_id = 112  # @112Greece user ID
            tweets = []
            
            self.logger.debug("Fetching latest tweets from @112Greece")
            
            async for tweet in api.user_tweets(user_id, limit=10):
                tweets.append(tweet)
            
            if not tweets:
                self.logger.debug("No tweets found")
                return
            
            # Sort by ID (newest first)
            tweets.sort(key=lambda t: t.id, reverse=True)
            
            # Process new tweets
            new_tweets_found = False
            for tweet in tweets:
                # Skip if we've already seen this tweet
                if tweet.id in self.seen_tweets:
                    continue
                
                # Skip if older than our last known tweet
                if self.last_tweet_id and tweet.id <= self.last_tweet_id:
                    continue
                
                # Mark as seen
                self.seen_tweets.add(tweet.id)
                new_tweets_found = True
                
                self.logger.info(f"New tweet found: ID {tweet.id}")
                
                # Parse the alert
                parsed_alert = self._parse_alert(tweet.rawContent)
                
                # Check if we should announce it
                if self._should_announce(parsed_alert):
                    announcement = self._create_announcement_text(parsed_alert)
                    
                    self.logger.info(f"Announcing alert: {announcement[:100]}...")
                    
                    # Wait for silence before announcing
                    max_wait = 60  # Maximum 60 seconds wait
                    wait_start = time.time()
                    while self.repeater.talking and (time.time() - wait_start) < max_wait:
                        await asyncio.sleep(1)
                    
                    # Announce the alert
                    try:
                        self.repeater.speak_with_piper(announcement)
                    except Exception as e:
                        self.logger.error(f"Error announcing alert: {e}")
                else:
                    self.logger.debug("Alert did not meet announcement criteria")
            
            # Update last seen tweet ID if we found new tweets
            if new_tweets_found and tweets:
                newest_id = tweets[0].id
                self.last_tweet_id = newest_id
                self._save_last_tweet_id(newest_id)
                
        except Exception as e:
            self.logger.error(f"Error checking for tweets: {e}", exc_info=True)
    
    def run(self):
        """
        Main background service loop.
        Periodically checks for new tweets from @112Greece.
        """
        self.logger.info(
            f"112 Greece Alerts service started (checking every {self.check_interval}s)"
        )
        
        # Initial check after a short delay
        self._stop_event.wait(10)
        
        while not self._stop_event.is_set():
            try:
                # Run the async tweet checking function
                asyncio.run(self._check_for_new_tweets())
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
            
            # Wait for next check interval (or until stop event)
            self._stop_event.wait(self.check_interval)
        
        self.logger.info("112 Greece Alerts service stopped")
    
    def cleanup(self):
        """Called on shutdown"""
        self.logger.info("Cleaning up 112 Greece Alerts module")
        # Save final state
        if self.last_tweet_id:
            self._save_last_tweet_id(self.last_tweet_id)
