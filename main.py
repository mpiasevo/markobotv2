import discord
import os
import key
import youtube_dl
from discord.ext import commands,tasks
from dotenv import load_dotenv

TOKEN = key.TOKEN
client = discord.Client()

load_dotenv()

# Get the API token from the .env file.
#DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(TOKEN)
