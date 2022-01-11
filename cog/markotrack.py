import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL

intent = discord.Intents().all()
client = discord.Client(intents=intents)

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

    @client.event
    async def on_message(message):
        global logger
        try:
            

    @commands.command(name = '' description = '')
    
    
def setup(bot):
    bot.add_cog(Admin(bot))
