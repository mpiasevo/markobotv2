import discord
from discord.ext import commands
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

bot.load_extension("music")

bot.run(TOKEN)
