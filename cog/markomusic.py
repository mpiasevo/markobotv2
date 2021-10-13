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

#Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''
#TOKEN = key.TOKEN #Dont think I need this line anymore


#These are the ytdl options and ffmpeg options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' #bind to ipv4 since ipv6 can cause issues sometimes
}
ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdl_format_options)

class VoiceConnectionError(commands.CommandError):
    """Custom Exception Class for Connection Errors"""
    print('Connection Error')

class InvalidVoiceChannel(VoiceConnectionError):
    """Custom Exception Class for Invalid Voice Channels"""
    print('Voice Channel Error')

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')

        #YTDL info dicts (data) have other useful information you might want
        #https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a sict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        
        #dealing with playlists
        if 'entries' in data:
            #take first item from a playlist
            data = data['entries'][0]

        #embed = discord.Embed(title="", description=f"Queued [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]", color=discord.Color.green())
        #await ctx.send(embed=embed)
        await ctx.send(f"[{data['title']}] Added to queue")

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)
     
    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlist
    simultaneously. 
    NOTE: When the bot disconnects from the Voice, it's instance will be destroyed"""

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')
    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None #Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                #Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300): #5 mins
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                print('Timeout Error')
                return self.destroy(self._guild)
            
            if not isinstance(source, YTDLSource):
                #Source was probably a stream (not downloaded)
                #So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing you request, Sorry! \n'
                                             f'```css\n[{e}]\n```')
                    continue
                
                source.volume = self.volume
                self.current = source

                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                #embed = discord.Embed(title="Now playing", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}])", color=discord.Color.green())
                #self.np = await self._channel.send(embed=embed)
                self.np = await self._channel.send(f"Now playing [{source.title}]")
                await self.next.wait()

                #Make sure the FFmpeg process is cleaned up
                source.cleanup()
                self.current = None
        
        def destroy(delf, guild):
            """Disconnect and cleanup the player"""
            return self.bot.loop.creat_task(self._cog.cleanup(guild))

class Music(commands.Cog):
    """Music Related Commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        
        try:
            del self.players[guild.id]
        except KeyError:
            pass
    
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

        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to voice channel, please make sure you are in a valid channel')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name ='join', aliases=['connect', 'j'], description="Connects markobot to voice channel")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ----------
        channel: discord.VoiceChannel [optional]
            The Channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("No channel to join, please say !join while in a voice channel")
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timeout')

        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timeout')
        #if (random.randint(0,1 == 0):
        #       await ctx.message.add_reaction('')
        await ctx.send(f'**Joined `{channel}`**')
        
    @commands.command(name='play', aliases=['pl'], description="Makes markobot play music!")
    async def play_(self, ctx, *, search: str):
        """Request a song to play (add to queue if already songs)
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, ID or URL
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)
        
        player = self.get_player(ctx)

        #If download is False, source will be a dict which will be used later to regather the stream.
        #IF download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='pause', aliases=['ps'], description="Pauses any music that is playing")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            #embed = discord.Embed(title="", description="I am not currently playing anything", color=discord.Color.green())
            #return await ctx.send(embed=embed)
            return await ctx.send("I am not currently playing anything to pause")
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send("Paused!")

    @commands.command(name='resume', aliases=['r'], description="Resumes the song that was playing")
    async def resume_(self, ctx):
        """Resumes the currently paused song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            #embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            #return await ctx.send(embed=embed)
            return await ctx.send("I am not connected to a voice channel")
        elif not vc.is_paused():
            await ctx.send("There is not a paused song")
            return

        vc.resume()
        await ctx.send("Resuming!")
    
    @commands.command(name='skip', aliases=['sk', 'next'], description="Skips to the next song in the queue")
    async def skip_(self, ctx):
        """Skip the song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            #embed = discord.Embed(title="", desciption="I'm not connected to a voice channel", color=discord.Color.green())
            #return await ctx.send(embed=embed)
            return await ctx.send("I am not connected to a voice channel!")
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()

    @commands.command(name='remove', aliases=['rm'], description="Removes a specified song from the queue")
    async def remove_(self, ctx, pos: int=None):
        """Removes specified song from the queue"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            #You can add the other version of this later
            return await ctx.send("I'm not connected to a voice channel, dummy!")
        
        player = self.get_player(ctx)
        if pos == None:
            player.queue._queue.pop()
        else:
            try:
                s = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                await ctx.send(f"Removed [{s['title']}]")
            except:
                await ctx.send(f"Could not find a track for '{pos}'")

    @commands.command(name='clear', aliases=['clr', 'cl'], description="Clears the entire queue")
    async def clear_(self, ctx):
        """Deletes entire queue of upcoming songs"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not connected to a voice channel, dummy!")

        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send("**Cleared Queue**")

    @commands.command(name='queue', aliases=['q', 'playlist'], decription="Shows the current song queue")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of the upcoming songs"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not connected to a voice channel, dummy!")

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send("The queue is empty...")

        seconds = vc.source.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh #02dm %02ds" % (hour, minutes, seconds)

        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        #Grabs the songs in the queue
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) | ` {duration} Requested by: {_['requester']}`\n" for _ in upcoming)
        fmt = f"\n__Now Playing__:\n[{vc.source.title}]({vc.source.web_url}) | ` {duration} Requested by: {vc.source.requester}`\n\n__Up Next:__\n" + fmt + f"\n**{len(upcoming)} songs in queue**"
        embed = discord.Embed(title=f'Queue for {ctx.guild.name}', description=fmt, color=discord.Color.green())
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='leave', aliases=["stop", "dc", "disconnect", "bye"], description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            #embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send("I can't leave if im not in a voice channel.")

        await ctx.send('**Successfully disconnected**')

        await self.cleanup(ctx.guild)




def setup(bot):
    bot.add_cog(Music(bot))
