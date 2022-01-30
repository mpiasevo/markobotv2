#This will be the file where the admin commands live
"""
To be added/readded:
    purge
I wonder if I can make the bot detect if csgo gets opened by someone :D`
"""
import discord
from discord.ext import commands
import random
import os
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
import sqlite3

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
        temp = {}
        db = sqlite3.connect('messages.sqlite')
        cursor = db.cursor()
        embed = discord.Embed(title="Message Stats", color=0xff0000)
        for mem in ctx.guild.members:
            cursor.execute("SELECT SUM(msgs) FROM main WHERE guild_id = ? AND user_id = ?",(f'"{ctx.guild}"',f'"{mem}"',))
            result = cursor.fetchone()
            if result[0] is None:
                pass
            else:
                temp[str(mem)]=result[0]
        sorttemp = sorted(temp.items(), key=lambda x: x[1], reverse = True)
        for value in sorttemp:
            if value[1] > 10:
                embed.add_field(name=value[0], value=f"{value[1]} messages sent", inline=False)
            else:
                pass
        await ctx.send(embed=embed)       
        cursor.close()
        db.close()

    @commands.command(name = 'update', description='update messages temp command')
    async def update_(self, ctx, name = ''):
        nmessages1 = 0
        member1 = name
        db = sqlite3.connect('messages.sqlite')
        cursor = db.cursor()
        if str(ctx.message.author) == "MP#4163":
            for chan in ctx.guild.text_channels:
                for mem in ctx.guild.members:
                    async for msg in chan.history(limit=None):
                        if str(msg.author) == str(mem):
                            nmessages1 += 1
                        else:
                            pass
                    print(ctx.guild, chan, mem, nmessages1)
                    cursor.execute(f'SELECT msgs FROM main WHERE guild_id = ? and channel_id = ? and user_id = ?', (f'"{ctx.guild}"', f'"{chan}"', f'"{mem}"',))
                    result = cursor.fetchone()
                    if result is None:
                        sql = ("INSERT INTO main(guild_id, channel_id, user_id, msgs) VALUES(?,?,?,?)")
                        val = (f'"{ctx.guild}"', f'"{chan}"', f'"{mem}"', nmessages1)
                        cursor.execute(sql, val)
                        db.commit()
                    elif result is not None:
                        sql = ("UPDATE main SET msgs = ? WHERE guild_id = ? and channel_id = ? and user_id = ?")
                        val = (f'"{ctx.guild}"', f'"{chan}"', f'"{mem}"', nmessages1)
                        cursor.execute(sql, val)
                        db.commit()
                    nmessages1 = 0
        else:
            await ctx.send("You do not have permission to use this powerful command. Sorry")
        cursor.close()
        db.close()
        #print(ctx.message.guild, ctx.message.channel, member1, nmessages1)
    
    @commands.command(name = 'chart', description='Shows chart of data (messages, channels)')
    async def chart_(self, ctx, chart = ''):
        labels = []
        sizes = []
        temp = {}
        if chart == "messages":
            db = sqlite3.connect('messages.sqlite')
            cursor = db.cursor()
            for mem in ctx.guild.members:
                cursor.execute("SELECT SUM(msgs) FROM main WHERE guild_id = ? AND user_id = ?",(f'"{ctx.guild}"',f'"{mem}"',))
                result = cursor.fetchone()
                if result[0] is None:
                    pass
                elif result[0] < 10:
                    pass
                else:
                    temp[str(mem)]=result[0]
            #print(temp)
            sorttemp = sorted(temp.items(), key=lambda x: x[1], reverse = True)
            for value in sorttemp:
                labels.append(value[0])
                sizes.append(value[1])

            await asyncio.sleep(2)    
            #plt.pie(sizes, labels=labels, autopct=lambda p: '{:.2f}%\n({:.0f})'.format(p,(p/100)*sum(sizes)), shadow=False, startangle=90)
            colors = ['r','g','b','c','m','y']
            #plt.xticks(range(len(sizes)), labels)
            hbars = plt.barh(range(len(sizes)), sizes, color=random.choice(colors))
            plt.title(f'Messages Sent in {ctx.guild} by Each Member')
            plt.xlabel('Messages Sent')
            plt.yticks(range(len(sizes)), labels=labels)
            #plt.axis('equal') #equal aspect ratio ensures that pie is drawn as circle
            plt.tight_layout()
            #labels next to bar
            for i in range(len(sizes)):
                plt.annotate(str(sizes[i]), xy=(sizes[i]-20,i), ha='center', va='bottom')
            plt.savefig('messages.png')
            
            file = discord.File("messages.png", filename="messages.png")
            await ctx.send("Messages Sent:", file=file)

            plt.clf()
            plt.cla()
            plt.close()
            os.remove("messages.png")
            #print(labels)
            #print(sizes)
                
        else:
            print("Error selection")

def setup(bot):
    bot.add_cog(Admin(bot))

