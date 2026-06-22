import sqlite3
import discord

#1 initialize the db for first run of the bot
## create and read? 
def init_db():
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()

    #create the server_settings table if not exists
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS server_settings (
                   guild_id INTEGER PRIMARY KEY,
                   channel_id INTEGER NOT NULL
                   )
                   ''')
    
    #Initializing the scroll_logs table that will store the tiktoks/reels and data about it
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS scroll_logs (
                   message_id INTEGER PRIMARY KEY,
                   guild_id INTEGER NOT NULL,
                   author_id INTEGER NOT NULL,
                   platform TEXT NOT NULL,
                   timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (guild_id) REFERENCES server_settings(guild_id)
                   )
                   ''')
    
    conn.commit()
    conn.close()
    print("databse and tables initialized successfully")

#2 server settings for what discord the db is for and what chat and what users
## create read and update
def save_settings(guild_id, channel_id):
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()

    #insert a new row of guild(discord server) and or update channel if guild(discord server) already exists in db
    cursor.execute('''
                   INSERT INTO server_settings (guild_id, channel_id)
                   VALUES (?, ?)
                   ON CONFLICT(guild_id) DO UPDATE SET
                   channel_id = excluded.channel_id 
                   ''', (guild_id, channel_id))
    
    conn.commit()
    conn.close()
    print(f"Settings saved for Server {guild_id}: watching channel {channel_id}")

# Retrieves the authorized tracking channel ID for a designated server. (This lets bot know what discord is the message coming from)
def get_settings(guild_id):
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()

    cursor.execute('SELECT channel_id FROM server_settings WHERE guild_id = ?', (guild_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

#4 our db of tiktoks/reels
## read and update
def log_scroll(message_id, guild_id, author_id, platform):
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()

    try:
        # Try to append the link event to our logbook ledger
        cursor.execute('''
            INSERT INTO scroll_logs (message_id, guild_id, author_id, platform)
            VALUES (?, ?, ?, ?)
        ''', (message_id, guild_id, author_id, platform))
        conn.commit()
        print(f"Logged {platform} link from user {author_id}")
    except sqlite3.IntegrityError:
        # If message_id already exists, SQLite blocks it here, and we ignore it safely
        print(f"Duplicate link ignored: Message ID {message_id}")
    finally:
        conn.close()

def log_scroll_batch(records):
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()
    
    try:
        # INSERT OR IGNORE automatically drops duplicates without throwing errors
        # executemany keeps the entire batch transaction sitting in RAM buffer!
        cursor.executemany('''
            INSERT OR IGNORE INTO scroll_logs (message_id, guild_id, author_id, platform)
            VALUES (?, ?, ?, ?)
        ''', records)
        conn.commit() # The physical disk turns on and writes everything in ONE push here
        print(f"Batch Sync Complete: Flushed {len(records)} media items from RAM to disk ledger.")
    except sqlite3.Error as e:
        print(f"Database batch error encountered: {e}")
    finally:
        conn.close()

def get_all_logged_ids():
    conn = sqlite3.connect('scrolls.db')
    cursor = conn.cursor()
    # We only pull the message_id column to keep the data package tiny
    cursor.execute('SELECT message_id FROM scroll_logs')
    # Fetch all rows and convert them into a fast-lookup Python set
    ids_set = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids_set