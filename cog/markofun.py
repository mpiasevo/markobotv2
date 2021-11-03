# This will be the cog for other commands idk what exactly, but we will add ping pong command
import discord
from discord.ext import commands
import random
import time
import datetime as dt
import pandas_datareader as web
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
#import youtube_dl
#from youtube_dl import YoutubeDL

intents = discord.Intents().all()
client = discord.Client(intents=intents)

class Fun(commands.Cog):
    """Fun Related Commands."""

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
    
#    @commands.command(name ='purge', description="Purges messages from a channel")
#    async def delete_(self, ctx, *, amount = 1):
#        """Purges a specified amount of messages from a channel.
#        Parameters
#        ----------
#        number: number of messages [optional]
#            The number of messages to delete, if no number is specified, 1 will be assumed"""
    @commands.command(name ='hello', aliases=['hi', 'hey'], description ='Say hi to markobot')
    async def hello_(self, ctx):
        """Say hello to markobot, sometimes he wishes more people would say hello :(
        Parameters
        ----------
        [NONE]
        """
        text = "Hello {}, thanks for saying hi :)".format(ctx.message.author)
        await ctx.send(text)

    @commands.command(name='flip', aliases=['coinflip'], description ='Flip a coin')
    async def coinflip_(self, ctx, choice = 'tails'):
        """Flip a coin, don't forget to choose heads or tails
        Parameters
        ----------
        defaults to tails (never fails)
        heads = chooses heads
        tails = chooses tails
        """
        options = ["heads","tails"]
        result = random.choice(options)
        await ctx.send("Flipping a virtual coin...")
        time.sleep(1)
        if choice == "heads" or choice == "tails":

            if choice == result:
                text = "You win, you chose **{}** the result was **{}**".format(choice, result)
            else:
                text = "You lose, you chose **{}** and the result was **{}**".format(choice, result)
        else:
            text = "The only sides on a coin are heads and tails, you chose **{}**".format(choice)
        #text = "The result is **{}**".format(result)
        await ctx.send(text)

    @commands.command(name='cprice', description='Check the price of your Crypto')
    async def crypto_(self, ctx, crypto = 'BTC'):
        """Check the price of your crypto.
        Parameters
        ----------
        defaults to BTC
        !cprice [crypto] to choose a crypto
        """
        try:
            start = (dt.datetime.now() + dt.timedelta(days=-1)) #DataReader parameter
            end = dt.datetime.now() #DataReader parameter
            crypto = crypto.upper() #Make user input uppercase
            search = crypto+'-USD' #DataReader parameter
            ltc = web.DataReader(search,'yahoo', start, end) #DataReader search
            price = ltc.iloc[0]['Close'] #price of crypto
            volume = ltc.iloc[0]['Volume'] #volume of crypto sold on that date
            date = end.strftime("%m/%d/%y") #format date correctly
            text = "**{}** is priced at **${:,.2f}** with a volume of **{:,}** traded on **{}**".format(crypto,price,volume,date)
            await ctx.send(text)
        except:
            await ctx.send("**{}** is an invalid cryptocurrency, sorry.".format(crypto))
def setup(bot):
    bot.add_cog(Fun(bot))

