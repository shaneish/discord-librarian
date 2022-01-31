import discord
from discord.ext import commands
from utils import  and_includes, or_includes
import random
import requests
from datetime import datetime, timedelta
import sys


class Creeper(commands.Cog):
    """
    Creeper just peeps messages and responds with group in-jokes
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if and_includes(message.content, 'thank', 'soros'):
            # Responds to Sal when he says 'Thanks Soros'
            # (note: not antisemitic joke, used to mock the antisemitic globalist Soros stories)
            await message.channel.send('No problemo buckaroo, anything for a fellow reptile.')
        
        if and_includes(message.content, 'who', 'horrible') and (random.random() < 0.5):
            # You know what this does
            await message.channel.send(f"Why, {message.author.mention} of course!")

        if or_includes(message.content, 'socialis', 'communis') and (random.random() < 0.33):
            # You know what this does
            await message.channel.send(f"AJ is the real commie here!")
        
        if or_includes(message.content, 'shane', 'metricity', 'the best') and (message.author != self.bot.user) and (random.random() < 0.333):
            await message.channel.send(f"Shane really is the best.")
        
        if or_includes(message.content, "suck", "sux") and (message.author != self.bot.user) and (random.random() < 0.333):
            # ya know what this does too
            await message.channel.send("You know what else sucks? Salex Bexman.")
        
        if ('twitter' in message.content.lower()) and (random.random() < 0.25):
            if 'metricity' in message.author.name.lower():
                await message.channel.send(f"Another well-researched Shaun King tweet, {message.author.mention}?")
            elif 'mudman' in message.author.name.lower():
                await message.channel.send(f"Inta Hmar, {message.author.mention}.")

    @commands.command()
    async def test(self,ctx):
        await ctx.send("Stop spamming the fucking chat with your damn tests u chode.")


class Utes(commands.Cog):

    @commands.command()
    async def gif(self, ctx, *args):
        # returns random gifs
        scope, args = (int(args[0]), args[1:]) if args[0].isdigit() else (1, args)
        num_gifs, args = (scope, args[1:]) if args[0] == 'melee' else (1, args)
        search = "+".join(args)
        choice = random.randint(1, scope)
        response = requests.get(f"https://api.giphy.com/v1/gifs/search?q={search}&api_key=WiLstLIo2SInusTmGDDkhhY0tU6xKNEl&limit={num_gifs}&offset={choice}")
        if response.status_code != 200:
            await ctx.send("U stupid bruh, bad request.")
        else:
            gifs = response.json()['data']
            gif_urls = [gif['url'] for gif in gifs]
            for url in gif_urls:
                await ctx.send(url)

    @commands.command()
    async def calc (self, ctx, *args):
        #check args
        async with ctx.channel.typing(): #makes the channel say the bot is typing
            terms = " ".join(args)
            await ctx.channel.send(eval(terms))


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.UserInputError):
            await ctx.send('There was an error in the command.')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)


class RateLimiter(commands.Cog):
    def __init__(self):
        self.last_check_in = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        #TODO: Put some random fuzz on the checkin timedelta
        #TODO: Lower the checkin time delta based on the subsequent frequency
        if isinstance(message.channel, discord.channel.DMChannel) or isinstance(message.channel, discord.channel.GroupChannel):
            return
        if not self.last_check_in or self.last_check_in < (message.created_at - timedelta(seconds = 60)):
            #grab the non-bot members
            memb_ls=[m for m in message.channel.members if not m.bot]
            #grab the last ten minutes of messages, up to 600 messages
            self.last_check_in = message.created_at
            ten_min_ago = message.created_at - timedelta(seconds = 600)
            messages = await message.channel.history(limit = 600, after = ten_min_ago).flatten()
            #get the history of message authors who aren't bots
            human_authors_history = [m.author for m in messages if m.author in memb_ls] 
            #get the unique authors
            human_author_set = set(human_authors_history)
            #if two users are talking
            prefix = None
            if len(human_author_set) == 2:
                prefix = f"{list(human_author_set)[0].mention} and {list(human_author_set)[1].mention} are "
            #if one user is talking to themself
            elif len(human_author_set) == 1:
                prefix = f"{list(human_author_set)[0].mention} is "
            if prefix:
                if len(messages) > 50:
                    await message.channel.send(prefix + "going at it. Wow!")
                if len(messages) > 100:
                    await message.channel.send(prefix + "getting into some serious behavior.")
                if len(messages) > 150:
                    await message.channel.send(prefix + "setting a record!")
                if len(messages) > 200:
                    await message.channel.send(prefix + "very serious about this!")
                if len(messages) > 250:
                    await message.channel.send(prefix + ", shut up. Please.")