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

class Track(commands.Cog):
    """Tracking Related Commands"""

    __slots__ = ('bot', 'players')

    def __init__(self,bot):
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
                return await ctx.send('This commands cannot be used in private messages.')
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
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

    # @commands.command(name = 'setaward', description='A command to setup awards')
    # async def stats_(self, ctx):
    #     #Setup roles command
    #     if ctx.message.author.guild_permissions.manage_messages == True:


    #     else:


       
def setup(bot):
    bot.add_cog(Track(bot))
