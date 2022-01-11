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
import main3
import matplotlib.pyplot as plt

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
    
    @commands.command(name = 'stats', description='Shows you your server stats!')
    async def stats_(self, ctx):
        temp = sorted(main3.track.items(), key=lambda x: x[1], reverse = True)
        embed = discord.Embed(title="Message Stats", color=0xff0000)
        for value in temp:
            embed.add_field(name=value[0], value=f"{value[1]} messages sent", inline=False)
        await ctx.send(embed=embed)       
        #await ctx.send('{} has sent {} messages (that I know of).'.format(ctx.message.author, temp))
    
    @commands.command(name = 'update', description='update messages temp command')
    async def update_(self, ctx, name = ''):
        nmessages1 = 0
        member1 = name
        #for mem in ctx.guild.members:
        #    print(mem)
        async for msg in ctx.channel.history(limit=None):
                #if msg.author == ctx.message.author:
            if str(msg.author) == member1:
                nmessages1 += 1
        print(ctx.message.channel, member1, nmessages1)
    
    @commands.command(name = 'chart', description='Shows chart of data (messages, channels)')
    async def chart_(self, ctx, chart = ''):
        labels = []
        sizes = []
        if chart == "messages":
            await asyncio.sleep(2)
            temp = main3.track.items()
            for value in temp:
                labels.append(value[0])
                sizes.append(value[1])
            
            plt.pie(sizes, labels=labels, autopct=lambda p: '{:.2f}%\n({:.0f})'.format(p,(p/100)*sum(sizes)), shadow=False, startangle=90)
            plt.axis('equal') #equal aspect ratio ensures that pie is drawn as circle
            plt.savefig('messages.png')
            
            file = discord.File("messages.png", filename="messages.png")
            
            #embed = discord.Embed(Title="Messages Sent", color=0xff0000)
            #embed.set_image(url="attachment://messages.png")

            await ctx.send("Messages Sent:", file=file)

            #print(labels)
            #print(sizes)
                
        else:
            print("Error selection")

def setup(bot):
    bot.add_cog(Admin(bot))

