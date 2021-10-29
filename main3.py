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

TOKEN = key.TOKEN
bot = commands.Bot(command_prefix='!')
bot.load_extension("cog.markomusic")
bot.load_extension("cog.markoadmin")
bot.load_extension("cog.markofun")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('you. !help'))
    print('We have logged in as {0.user}'.format(bot))

bot.run(TOKEN)


