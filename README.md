# how many scrolls Discord bot

Discord bot saving and counting how many tiktoks/reels were sent by a person on a discord channel

## Prerequisites
- **Python 3.8+ and SQLite3**
- **Libraries:** `discord.py`, `python-dotenv`, `sqlite3`

## Core Architectural Features
- **Multi-Tenant Relational Database Architecture:** Engineered using an optimized SQLite3 schema designed to dynamically isolate tracking configurations across multiple, separate Discord servers. Rather than using rigid local text configurations, the platform leverages unique `guild_id` indexing scopes to map server settings dynamically, providing secure cross-server data sandboxing from a single deployment instance.
- **High-Performance Backward Ingestion Pipeline:** Re-architected the historical synchronization (`!sync`) command to parse data backwards from the present moment using structured `asyncio` network streams. Tested against 90,000+ messages chat, the pipeline successfully extracted and indexed 8,100+ media links in under 10 minutes—maintaining a processing velocity of ~150 messages per second. The engine tracks structural duplicates completely in system memory using a fast-lookup RAM `set`, batching only fresh links before triggering high-efficiency multi-row inserts (`INSERT OR IGNORE`) to completely bypass heavy physical disk I/O bottlenecks.
- **Asynchronous Event Handling:** Utilizing `asyncio`, the application listens to live Discord WebSockets, dynamically detecting incoming content streams and incrementing metrics in real time without blocking the execution loop or introducing network latency.
- **Security Token Isolation:** Adheres to security standards by completely separating sensitive infrastructure tokens (such as your Discord Client Credentials) out of the main logic stream using environment variables (`.env`) kept safe via explicit `.gitignore` rules.
- **Normalized Link Matching:** Automatically handles string capitalization issues by forcing message streams to lower-case values before evaluating content sub-strings, ensuring link detection accuracy.




## Installation & Execution
1. **Click on the download link to add the bot to your discord server:**
https://discord.com/oauth2/authorize?client_id=1514230627250081813&permissions=68608&integration_type=0&scope=bot

2. **Initialize tracking:**
Go to the text channel where you want to log media links and type `!setup`. This links your discord channel to the database.

3. **Sync Historical Archives:** Type `!sync` to import the channel's past links into the database.  
   *Note: The first run can take some time depending on your channel's total message count. Don't worry, it isn't bugged, it's just thoroughly analyzing the history! Later syncs will be lightning fast because the bot's automatically stops scanning once it detects too many consecutive duplicate entries.*

### How It Works
When the bot is online, it tracks the designated Discord channel live. New media links are instantly processed and committed to the database, which the bot confirms visually by reacting with a `✅`.

### Checking Statistics
Use the `!help` command to see a full list of available commands and explore everything you can do with your collected data.

## Future Improvements
1. **High Priority**
- **Add a `!help` Command:** Build a clean help menu inside the chat so users can see all available commands as the bot gets bigger.
- **Time & Date Stats:** Save the exact date and time when a link is sent. This lets us build new commands to show stats like: How many links were sent this week? This month? What is the daily average?
- **Add queries:** Add queries for statistics like how many links overall on discord? how much from this specific user? what are his monthly stats?
2. **Medium Priority**
- **Clearer answers from the bot:** For example when the bot is done with !sync let it print on the discord chat how many links were updated to the db and how much failed if any and which one it was that failed.
- **Multi-Channel Clustering:** Change the configuration layer to utilize a composite primary key, enabling multi-channel indexing per discord server while maintaining speed and low overload (bot follows multiple chats u select in the discord).
3. **Low Priority**
- **Hidden Discord Log Channel:** Add a feature that sends a quiet message to a private staff channel whenever a link is counted. This lets you check if the bot is working perfectly without needing to look at your computer's terminal console.
- **Screen Time Calculator:** Look into a way to parse the shared links, find out how long the video is, and calculate exactly how many minutes of video your friend has sent to the chat.
- **Progress Charts:** Use a Python chart library to turn the database stats into visual graphs, showing how a user's link-sending habits progressed month over month.