import discord
import os
import database
from dotenv import load_dotenv
load_dotenv()

class MyClient(discord.Client):
    admin_id = int(os.getenv('ADMIN_ID'))
    target_id = int(os.getenv('TARGET_ID'))
    links_channel_id = int(os.getenv('LINKS_CHANNEL_ID'))

    async def on_ready(self):
        print(f'Hi im {self.user}, Im ready to count the scrolls!')

    async def on_message(self, message):
        if self.target_id == message.author.id:
            #getting rid of capitalization issues by making all message content lowercap
            content_lower = message.content.lower()
            tiktok = 'tiktok.com'
            reel = 'instagram.com'
            if tiktok in content_lower:
                print(f"{tiktok} found adding +1 tiktok to the scrolling grind")
                #executing the database.py so that we permanently save the data about the tiktok count 
                database.increment_count('tiktok')
            if reel in content_lower:
                print(f"{reel} found adding +1 reel to the scrolling grind")
                #executing the database.py so that we permanently save the data about the reel count
                database.increment_count('reel')

        if self.admin_id == message.author.id:
            content_lower = message.content.lower()
            if message.content == '!sync':
                print("deleting the db data so that we wont get double count while syncing")
                deleted_data = database.reset_db()

                sync_tiktoks = 0
                sync_reels = 0
                processed_messages = 0  # Our heartbeat tracker
                target_channel = self.get_channel(self.links_channel_id)

                print("Starting historical sync... (scanning the whole discord for tt/reels links and counting them)")
                async for old_msg in target_channel.history(limit=None):
                    processed_messages += 1
                    
                    # Every 5,000 messages, print a status heartbeat
                    if processed_messages % 5000 == 0:
                        print(f"🔄 Processed {processed_messages} (Found so far: {sync_tiktoks} tiktoks, {sync_reels} reels)")

                    if self.target_id == old_msg.author.id:
                        old_content_lower = old_msg.content.lower()
                        tiktok = 'tiktok.com'
                        reel = 'instagram.com'

                        if tiktok in old_content_lower:
                            sync_tiktoks += 1

                        if reel in old_content_lower:
                            sync_reels += 1

                database.save_final_count(sync_tiktoks, sync_reels)
                print(f"deleted {deleted_data} during the !sync")
                print(f"Successfully found and counted {sync_tiktoks} tiktoks and {sync_reels} reels")


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.getenv('DISCORD_TOKEN'))
