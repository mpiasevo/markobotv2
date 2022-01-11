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

intents = discord.Intents().all()
client = discord.Client(intents=intents)

TOKEN = key.TOKEN
bot = commands.Bot(command_prefix='!')
bot.load_extension("cog.markomusic")
bot.load_extension("cog.markoadmin")
bot.load_extension("cog.markofun")

messages = joined = 0
track = {}
member = "MP#4163"
nmessages = 0
#async for message in ctx.channel.history():
#    if message.author == member:
#        nmessages += 1
#    print(nmessages)

@bot.event
async def on_ready():
    global track
    await bot.change_presence(activity=discord.Game('you. !help'))
    print('We have logged in as {0.user}'.format(bot))
    
    with open("stats.txt", "r") as f:
        first = f.read().split('\n',1)[0]
        result = first.split(';')[1]
        print(result)
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
    if message_author in track:
        track[f"{message.author}"] += 1
        print(track)
    else:
        track[f"{message.author}"] = 1

bot.loop.create_task(update_stats()) #runs function in the background on loop

bot.run(TOKEN)


