import discord
import os
import database
from dotenv import load_dotenv
load_dotenv()

class MyClient(discord.Client):

    async def on_ready(self):
        database.init_db()
        print(f'Hi im {self.user}, Im ready to count the scrolls!')

    #make func to include the sqldb so that the tiktoks get appended there
    async def on_message(self, message):

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

                if platform:
                    if old_msg.id in known_ids: 
                        consecutive_duplicates += 1
                    else:
                        consecutive_duplicates = 0 # Reset! We found a fresh, missing link!
                        sync_RAMcache.append((old_msg.id, message.guild.id, old_msg.author.id, platform))
                
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
     

#below is everything to make the bot run and get data using API and read messages
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.getenv('DISCORD_TOKEN'))
