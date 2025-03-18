"""
Script: rss2supabase.py
Author: drhdev
Version: 0.1
License: GNU Public License v3

Description:
This script reads an RSS feed, processes entries, and stores only new ones in a Supabase database.
It ensures data integrity, retries on network failures, and logs every step for debugging.
Environment variables are used for secure API credentials, and UTF-8 encoding is enforced.
"""

import os
import time
import logging
import feedparser
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from requests.exceptions import RequestException
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RSS_FEED_URL = os.getenv("RSS_FEED_URL")

# Configure logging
LOG_FILE = "rss_feed_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",  # Overwrite on each run
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.info("Script started.")

# Ensure API credentials are set
if not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("Missing Supabase credentials in .env file.")
    exit("Supabase credentials are required in .env file.")

# Ensure RSS Feed URL is set
if not RSS_FEED_URL:
    logging.error("Missing RSS feed URL in .env file.")
    exit("RSS feed URL is required in .env file.")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logging.info("Connected to Supabase.")
except Exception as e:
    logging.error(f"Failed to connect to Supabase: {e}")
    exit("Supabase connection failed.")


def fetch_rss_feed(url, retries=3, delay=5):
    """Fetch and parse the RSS feed with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            if feed.bozo:
                raise ValueError("Malformed RSS feed.")
            return feed
        except (RequestException, ValueError) as e:
            logging.warning(f"Attempt {attempt}: Failed to fetch RSS feed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                logging.error("Max retries reached. Exiting.")
                exit("Failed to fetch RSS feed.")


def entry_exists(title, pub_date):
    """Check if the entry is already in the database."""
    try:
        result = (
            supabase.table("rss_entries")
            .select("title, published")
            .eq("title", title)
            .eq("published", pub_date)
            .execute()
        )
        return len(result.data) > 0
    except Exception as e:
        logging.error(f"Database check failed: {e}")
        return False


def store_entry(title, content, pub_date, link):
    """Store a new RSS entry in the database."""
    try:
        supabase.table("rss_entries").insert(
            {
                "title": title,
                "content": content,
                "published": pub_date,
                "link": link,
            }
        ).execute()
        logging.info(f"Stored new entry: {title}")
    except Exception as e:
        logging.error(f"Failed to store entry: {e}")


def process_feed(feed):
    """Process RSS feed entries."""
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        content = entry.get("summary", "").strip()
        pub_date = entry.get("published", "").strip()
        link = entry.get("link", "").strip()

        # Ensure UTF-8 encoding
        title = title.encode("utf-8", "ignore").decode("utf-8")
        content = content.encode("utf-8", "ignore").decode("utf-8")
        pub_date = pub_date.encode("utf-8", "ignore").decode("utf-8")
        link = link.encode("utf-8", "ignore").decode("utf-8")

        if not title or not link or not pub_date:
            logging.warning("Skipping entry with missing required fields.")
            continue

        if not entry_exists(title, pub_date):
            store_entry(title, content, pub_date, link)
        else:
            logging.info(f"Skipping already stored entry: {title}")


if __name__ == "__main__":
    logging.info("Fetching RSS feed...")
    rss_feed = fetch_rss_feed(RSS_FEED_URL)
    process_feed(rss_feed)
    logging.info("Script completed.")
