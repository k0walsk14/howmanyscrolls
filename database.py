import sqlite3
import json

def reset_db():
    with open('counts.json', 'r') as file:
        old_data = json.load(file)

    blank_data = {
        "tiktok": 0,
        "reel": 0
    }
    with open('counts.json', 'w') as file:
        json.dump(blank_data, file, indent=4)
    
    return old_data

#platform because we can execute the function with either platform == 'tiktok' or 'reel'
def increment_count(platform):

    #open the db file and get current scores from there to RAM
    with open('counts.json', 'r') as file:
        data = json.load(file)

    #update the score with what discordbot has counted
    data[platform] +=1

    #save the appended count back to the file so that it stays permanent
    with open('counts.json', 'w') as file:
        json.dump(data, file, indent=4)

def save_final_count(tiktok_total, reel_total):
    final_data = {
        "tiktok": tiktok_total,
        "reel": reel_total
    }
    with open('counts.json', 'w') as file:
        json.dump(final_data, file, indent=4)