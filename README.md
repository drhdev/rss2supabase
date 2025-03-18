# RSS2Supabase

## Overview

**RSS2Supabase** is a Python script that fetches an RSS feed, processes new entries, and stores them in a **Supabase** database. It ensures data integrity, retries on network failures, and logs each step for debugging.

## Features

- Fetches and parses RSS feeds.
- Avoids duplicates by checking existing entries in Supabase.
- Implements error handling and retry logic for network failures.
- Logs all actions for debugging.
- Uses UTF-8 encoding to prevent character corruption.
- Secure API credentials using `.env` file.

## Prerequisites

- Python 3.8+
- A **Supabase** account
- An active RSS feed URL

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rss2supabase.git
cd rss2supabase
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory and add:

```ini
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-api-key
RSS_FEED_URL=https://example.com/rss.xml
```

### 4. Run the Script

```bash
python rss2supabase.py
```

## Database Schema (Supabase)

Make sure you have a `rss_entries` table in your Supabase database:

```sql
CREATE TABLE rss_entries (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE
);
```

## Logging

The script generates a `rss2supabase.log` file in the working directory, which is overwritten each time the script runs.

## License

This project is licensed under the **GNU Public License v3**.

