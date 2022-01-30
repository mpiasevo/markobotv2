#Welcome to Version 3 of markobot 
#Testing cog for commands and queues
import discord
from discord.ext import commands
import time
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL
import key
import matplotlib.pyplot as plt
import sqlite3


intents = discord.Intents().all()
intents.members = True
client = discord.Client(intents=intents)

TOKEN = key.TOKEN
bot = commands.Bot(command_prefix='!', intents=intents)
bot.load_extension("cog.markomusic")
bot.load_extension("cog.markoadmin")
bot.load_extension("cog.markofun")

messages = joined = 0
track = {}
member = "MP#4163"
nmessages = 0

@bot.event
async def on_ready():
    global track
#    db = sqlite3.connect('messages.sqlite') ######Initial database setup
#    cursor = db.cursor()
#    cursor.execute('''
#            CREATE TABLE IF NOT EXISTS main(
#            guild_id TEXT,
#            channel_id TEXT,
#            user_id TEXT,
#            msgs INTEGER
#            )
#            ''')
    await bot.change_presence(activity=discord.Game('you. !help'))
    print('We have logged in as {0.user}'.format(bot))
    
    with open("stats.txt", "r") as f:
        first = f.read().split('\n',1)[0]
        result = first.split(';')[1]
        #print(result)
        track = eval(result)
        print(track)

@bot.event
async def update_stats():
    await bot.wait_until_ready()
    await asyncio.sleep(5)
    global messages, joined, track
    
    while not bot.is_closed():
        try:
            with open("stats.txt", "w") as f:
                f.write(f"Messages;{track}\n")
            messages = 0
            joined = 0
            
            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)                                  
    
@bot.event
async def on_member_join(member):
    global joined
    joined += 1

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    global track
    global messages
    message_author = (f"{message.author}")
    message_author2 = (f'"{message.author}"')
    message_guild = (f'"{message.guild}"')
    message_channel = (f'"{message.channel}"')
    db = sqlite3.connect('messages.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT msgs FROM main WHERE guild_id = ? and channel_id = ? and user_id = ?', (message_guild, message_channel, message_author2,))
    result = cursor.fetchone()
    print(result)
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, user_id, msgs) VALUES(?,?,?,?)")
        val = (message_guild, message_channel, message_author2, 1)
        cursor.execute(sql, val)
        db.commit()
    elif result is not None:
        sql = ("UPDATE main SET msgs = msgs + 1 WHERE guild_id = ? and channel_id = ? and user_id = ?")
        val = (message_guild, message_channel, message_author2)
        cursor.execute(sql, val)
        db.commit()
    cursor.close()
    db.close()

    if message_author in track:
        track[f"{message.author}"] += 1
        print(track)
    else:
        track[f"{message.author}"] = 1

bot.loop.create_task(update_stats()) #runs function in the background on loop

bot.run(TOKEN)
