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
bot.load_extension("cog.markotrack")

messages = joined = 0
member = "MP#4163"
nmessages = 0

@bot.event
async def on_ready():
#    db = sqlite3.connect('messages.sqlite') ######Initial database setup
#    cursor = db.cursor()
#    cursor.execute('''
#            CREATE TABLE IF NOT EXISTS awards(
#            guild_id TEXT,
#            msgs INTEGER
#            )
#            ''')

    await bot.change_presence(activity=discord.Game('you. !help'))
    print('We have logged in as {0.user}'.format(bot))                                 
    
@bot.event
async def on_member_join(member):
    global joined
    joined += 1

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    global messages
    message_author = (f"{message.author}")
    message_author2 = (f'"{message.author}"')
    message_guild = (f'"{message.guild}"')
    message_channel = (f'"{message.channel}"')
    db = sqlite3.connect('messages.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT msgs FROM main WHERE guild_id = ? and channel_id = ? and user_id = ?', (message_guild, message_channel, message_author2,))
    result = cursor.fetchone()
    #print(result)
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

bot.run(TOKEN)
