#This will be the file where the admin commands live
"""
To be added/readded:
    purge
I wonder if I can make the bot detect if csgo gets opened by someone :D`
"""
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

intents = discord.Intents().all()
client = discord.Client(intents=intents)

class Admin(commands.Cog):
    """Admin Related Commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def __local_check(self, ctx, error):
        """A local check which applies to all commands in this cog"""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True
    
    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog"""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command cannot be used in private messages.')
            except discord.HTTPException:
                pass

        #elif isinstance(error, InvalidVoiceChannel):
        #    await ctx.send('Error connecting to voice channel, please make sure you are in a valid channel')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    @commands.command(name ='purge', description="Purges messages from a channel")
    async def delete_(self, ctx, *, amount = 1):
        """Purges a specified amount of messages from a channel.
        Parameters
        ----------
        number: number of messages [optional]
            The number of messages to delete, if no number is specified, 1 will be assumed"""

        if ctx.message.author.guild_permissions.manage_messages == True:
            await ctx.channel.purge(limit=amount+1)
            print(ctx.guild,':', ctx.channel, 'has just been purged:', amount, 'messages were deleted by:', ctx.message.author)

        else:
            text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
            await ctx.send(text)

def setup(bot):
    bot.add_cog(Admin(bot))

