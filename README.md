# how many scrolls Discord bot

Discord bot saving and counting how many tiktoks/reels were sent by a person on a discord channel

## Prerequisites
- **Python 3.8+ and SQLite3**
- **Libraries:** `discord.py`, `python-dotenv`

## Core Architectural Features
- **Memory-Optimized Historical Synchronization:** The `!sync` engine is architected to process massive chat streams (scanning a 7-year history of 90k+ messages) entirely within system RAM. This eliminates heavy disk I/O bottlenecks by accumulating link frequencies in volatile memory before executing a single, clean batch-commit at completion.
- **Asynchronous Event Handling:** Utilizing `asyncio`, the application listens to live Discord WebSockets, dynamically detecting incoming content streams and incrementing metrics in real time without blocking the execution loop or introducing network latency.
- **Security & Configuration Separation:** Adheres to enterprise security standards by separating infrastructure keys, Discord API tokens, and user target IDs away from the core logic using environment variables (`.env`).
- **Normalized Link Matching:** Automatically handles string capitalization issues by forcing message streams to lower-case values before evaluating content sub-strings, ensuring link detection accuracy.

## Installation & Execution
1. **Clone the repository to your local workspace:**
```bash
git clone https://github.com/k0walsk14/howmanyscrolls
cd howmanyscrolls
```
2. ## Configure your environment variables
Create a `.env` file in the root directory and map your configuration keys exactly like this:
```env
DISCORD_TOKEN=your_bot_token_here
ADMIN_ID=your_discord_user_id
TARGET_ID=friend_user_id_to_track
LINKS_CHANNEL_ID=target_channel_id_to_scan
```
3. **Execute directly through the terminal**
```bash
python howmanyscrolls.py
```

4. **How to use**
- For first run please use !sync on chat so that the bot looks through the whole chat, counting and saving the tiktoks/reels into the database.
- After that as long as the bot runs newly sent tiktoks will be added automatically.

## Future Improvements
1. **High Priority**
- **Move from JSON to SQLite3:** Replace counts.json with a real SQLite3 database. Right now, writing to a JSON file overwrites the whole file every single time, which can corrupt your data if the bot scales up.
- **Smart Syncing (No more data wiping):** Get rid of the current reset_db() setup. Once the bot uses SQLite3 to track unique message IDs and dates, the !sync command can just check for new messages instead of deleting everything and counting from scratch.
- **Time & Date Stats:** Save the exact date and time when a link is sent. This lets us build new commands to show stats like: How many links were sent this week? This month? What is the daily average?
2. **Medium Priority**
- **Track Multiple People:** Expand the code so it doesn't just track one friend. Update the system so it can count links for all users in the discord chat separately.
- **Add Twitter/X Support:** Update the link scanner so it doesn't just look for TikTok and Reels, but tracks Twitter/X links too.
- **Add a `!help` Command:** Build a clean help menu inside the chat so users can see all available commands as the bot gets bigger.
3. **Low Priority**
- **Hidden Discord Log Channel:** Add a feature that sends a quiet message to a private staff channel whenever a link is counted. This lets you check if the bot is working perfectly without needing to look at your computer's terminal console.
- **Screen Time Calculator:** Look into a way to parse the shared links, find out how long the video is, and calculate exactly how many minutes of video your friend has sent to the chat.
- **Progress Charts:** Use a Python chart library to turn the database stats into visual graphs, showing how a user's link-sending habits progressed month over month.