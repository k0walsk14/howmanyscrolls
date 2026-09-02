import discord
import os
import database
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

#testing
#BLOCKED_GUILD_IDS = {
    #627962294214721546
#}

class MyClient(discord.Client):

    #add a first launch function that sends what to do like tells them that they need to do !setup and then !sync

    async def on_guild_join(self, guild):
        #if guild.id in BLOCKED_GUILD_IDS:
            #return

        #check if they have a channel that server owners can enable an option for it to be a system_channel then send there
        if guild.system_channel:
            permissions = guild.system_channel.permissions_for(guild.me)

            if permissions.send_messages:
                await guild.system_channel.send(
                    "Hi! I'm HowManyScrolls, a bot that tracks shared social-media links "
                    "so you can find them again later and display different statistics. \n\n"

                    "**Getting started:**\n"
                    "1. An administrator runs `!setup` in the channel you want me to monitor.\n"
                    "2. Run `!sync` to scan that channel's earlier messages.\n"
                    #"3. Run `!help` to see all the cool features and statistics i can display!\n\n"

                    "**Note:** The first `!sync` may take a while in channels with a large "
                    "message history. During the scan, I only check that selected channel "
                    "for supported social-media links and save matching entries to the database.\n\n"
                    "After the first sync, I will track supported links automatically while "
                    "I am online. If I am offline, just run `!sync` again "
                    "after I come back online to catch up on new links."   
                )
                return

        #send the welcome message to the first possible text channel where the bot has perms to send messages
        for channel in guild.text_channels:
            permissions = channel.permissions_for(guild.me)

            if permissions.send_messages:
                await channel.send(
                    "Hi! I'm HowManyScrolls, a bot that tracks shared social-media links "
                    "so you can find them again later and display different statistics. \n\n"
                    
                    "**Getting started:**\n"
                    "1. An administrator runs `!setup` in the channel you want me to monitor.\n"
                    "2. Run `!sync` to scan that channel's earlier messages.\n"
                    #"3. Run `!help` to see all the cool features and statistics i can display!\n\n"
                    
                    "**Note:** The first `!sync` may take a while in channels with a large "
                    "message history. During the scan, I only check that selected channel "
                    "for supported social-media links and save matching entries to the database.\n\n"  
                    "After the first sync, I will track supported links automatically while "
                    "I am online. If I am offline, just run `!sync` again "
                    "after I come back online to catch up on new links."   
                )
                return

        

    async def on_ready(self):
        print(f'Hi im {self.user}, Im ready to count the scrolls!')

    #make func to include the sqldb so that the tiktoks get appended there
    async def on_message(self, message):

        #if message.guild is None or message.guild.id in BLOCKED_GUILD_IDS:
            #return

        #anti-bot shield, ignore all messages from bots/apps (faster processing, lower message count)
        if message.author.bot:
            return
        
        
        #parse the content into list of arguments
        content = message.content.strip()
        args = content.split()
        if not args:
            return
        
        command = args[0].lower()

        #!setup logic to fill out save_settings() server_settings db

        if command == "!setup":
            #authorization check so that on only admins can do !setup
            if not message.author.guild_permissions.administrator:
                await message.channel.send('Admin permissions required to use "!setup"')
                return
            guild_id = message.guild.id
            channel_id = message.channel.id

            database.save_settings(guild_id, channel_id)

            await message.channel.send("Channel is now monitored by the db")

            return

        #lookup using get_settings that checks if incoming messages are coming from the text channel that is saved in sql db
        
        #check if there is any discord stored in the db server_settings if not return and print error
        target_channel_id = database.get_settings(message.guild.id)
        if target_channel_id is None:
            await message.channel.send('"!setup" has not been run yet. Please do so to link the bot to this discord channel.')
            return
        
        #check if the message was sent in the channel that is in the db server_settings if not return
        if target_channel_id != message.channel.id:
            return

        #!sync command that goes backward up to databases latest message ID, saves new entries into a RAM array, and flushes all at once via log_scroll_batch()
        if command == "!sync":
            await message.channel.send("Scanning for links...")
        
            known_ids = database.get_all_logged_ids()
        
            history_cursor = message.channel.history(limit=None, oldest_first=False)
        
            sync_RAMcache = []
            consecutive_duplicates = 0
        
            async for old_msg in history_cursor:
                if old_msg.author.bot:
                    continue
        
                if "http" not in old_msg.content:
                    continue
        
                old_lowered_content = old_msg.content.lower()
        
                #add a smart disabler that disables the !sync after it finds consecutive links that are already in the db. we do this because the !sync searches bottom to top now
        
                # Check if this message is a media link we care about
                platform = None
                if "tiktok.com" in old_lowered_content:
                    platform = "TikTok"
                elif "instagram.com/reel" in old_lowered_content:
                    platform = "Instagram"
                elif "x.com" in old_lowered_content or "twitter.com" in old_lowered_content:
                    platform = "Twitter"
                elif "youtube.com/shorts" in old_lowered_content:
                    platform = "Youtube"
        
                if platform:
                    if old_msg.id in known_ids: 
                        consecutive_duplicates += 1
                    else:
                        consecutive_duplicates = 0 # Reset! We found a fresh, missing link!
                        sync_RAMcache.append((old_msg.id, old_msg.guild.id, old_msg.author.id, platform))
                        
                        # If we've hit 50 media links in a row that we already know about, stop scanning!
                if consecutive_duplicates >= 50:
                    print("!Sync stopped. Caught up to historical data.")
                    break
        
                if len(sync_RAMcache) >= 100:
                    database.log_scroll_batch(sync_RAMcache)
                    sync_RAMcache.clear()
        
            if sync_RAMcache:  # This checks "if the list is not empty" just send them to db 
                database.log_scroll_batch(sync_RAMcache)
                        
            await message.channel.send("Synchronization complete! Archive is up to date.")
            return

        #filter to check if the message is a tiktok/reel/x and appends them live to log_scroll()
        lowered_content = message.content.lower()

        if "tiktok.com" in lowered_content:
            database.log_scroll(message.id, message.guild.id, message.author.id, "TikTok")
            await message.add_reaction("✅")

        elif "instagram.com/reel" in lowered_content:
            database.log_scroll(message.id, message.guild.id, message.author.id, "Instagram")
            await message.add_reaction("✅")

        elif "x.com" in lowered_content or "twitter.com" in lowered_content:
            database.log_scroll(message.id, message.guild.id, message.author.id, "Twitter")
            await message.add_reaction("✅")

        elif "youtube.com/shorts" in lowered_content:
            database.log_scroll(message.id, message.guild.id, message.author.id, "Youtube")
            await message.add_reaction("✅")

        #friend trolling below
        #if message.author.id == :
            #if "tiktok.com" in lowered_content or "instagram.com/reel" in lowered_content or "youtube.com/shorts" in lowered_content:
                #gif_url = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2UxYnlveWdyODFmYW1tcjZuMHB4N3U0ZzZiNGt6MDAwdGlza2ppbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/e5caWLx30Yjpi4urr4/giphy.gif"
                #await message.channel.send(f"{gif_url}")
                #return    

#below is everything to make the bot run and get data using API and read messages
database.init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = MyClient(intents=intents)

if not TOKEN:
    raise RuntimeError(
       "DISCORD_TOKEN is missing. Copy .env.example to .env and add your token." 
    )
client.run(TOKEN)
