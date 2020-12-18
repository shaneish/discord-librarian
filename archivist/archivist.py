import discord
from discord import *
from discord.ext import commands 
import asyncio
import tldextract
import requests
import json
from urllib.parse import urlparse
from utils import cprint, url_validator, load_paywalls, load_token, and_includes, or_includes, strip
import random
from ast import literal_eval
from datetime import datetime, timedelta


class Archivist(commands.Cog):
    def __init__(self, paywalled_sites):
        self.paywalled_sites = paywalled_sites

    @commands.command(name = 'paywall')
    async def archive_link(self, ctx, link: str):
        # Manually link to archive.is
        # Format: `!paywall URL` will link to archive.is/URL
        if url_validator(link):
            await ctx.send(f"https://www.archive.is/{link}")
        else:
            await ctx.send(f"**{link}** is an invalid url.")
    
    @commands.command()
    async def add(self,ctx, *new_paywalls):
        # Add new domains to list of paywalled domains
        # Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
        #     of paywalled sites and respond with a confirmation message.
        self.paywalled_sites = set(self.paywalled_sites).union(set(new_paywalls))
        async with open('paywalled', 'w') as file:
            sites = "\n".join(self.paywalled_sites)
            await file.write(sites)
            await ctx.send('**Added the following domains:**' + "\n" + cprint(new_paywalls))

    @commands.command()
    async def delete(self, ctx, *remove_sites):
        # Delete domains to list of paywalled domains
        # Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
        #     of paywalled sites and respond with a confirmation message.
        self.paywalled_sites = set(self.paywalled_sites).difference(set(remove_sites))
        async with open('paywalled', 'w') as file:
            sites = "\n".join(paywalled_sites)
            await file.write(sites)
            await ctx.send('**Deleted the following domains:**' + "\n" + cprint(remove_sites))
    
    @commands.command(name = 'list paywalls')
    async def list_paywalls(self, ctx, arg:str):
        await ctx.send("**Paywalled sites:**" + "\n" + cprint(sorted(paywalled_sites)))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks if message is a valid URL and a paywalled domain.  If it is, returns the archive.is link.
        if url_validator(message.content):
            raw_url = message.content
            url = tldextract.extract(message.content)
            if url.domain in paywalled_sites:
                await message.channel.send(f"https://www.archive.is/{raw_url}")


class RateLimiter(commands.Cog):
    def __init__(self):
        self.last_check_in = None

    @commands.Cog.listener()
    async def on_message(self, message: Message):
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
                if len(messages) > 100:
                    await message.channel.send(prefix + "going at it. Wow!")
                if len(messages) > 200:
                    await message.channel.send(prefix + "getting into some serious behavior.")
                if len(messages) > 300:
                    await message.channel.send(prefix + "setting a record!")
                if len(messages) > 400:
                    await message.channel.send(prefix + "very serious about this!")
                if len(messages) > 500:
                    await message.channel.send(prefix + ", shut up. Please.")

class Creeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if and_includes(message.content, 'thank', 'soros'):
            # Responds to Sal when he says 'Thanks Soros'
            # (note: not antisemitic joke, used to mock the antisemitic globalist Soros stories)
            await message.channel.send('No problemo buckaroo, anything for a fellow reptile.')
        
        if and_includes(message.content, 'who', 'horrible'):
            # You know what this does
            await message.channel.send(f"Why, {message.author.mention} of course!")

        if or_includes(message.content, 'socialis', 'communis'):
            # You know what this does
            await message.channel.send(f"AJ is the real commie here!")
        
        if or_includes(message.content, 'shane', 'metricity', 'the best')  and (message.author != self.bot.user):
            await message.channel.send(f"Shane really is the best.")
        
        if or_includes(message.content, "suck", "sux") and (message.author != self.bot.user):
            # ya know what this does too
            await message.channel.send("You know what else sucks? Salex Bexman.")

    @commands.command()
    async def test(self,ctx):
        await ctx.send("Stop spamming the fucking chat with your damn tests u chode.")
        
class Utes(commands.Cog):


    @commands.command()
    async def gif(self, ctx, *args):
        await ctx.send(f'Implement me. {cprint(args)}')
            # scope = 1
            # melee = False
            # num_gifs = 1
            # parsed = message.content.split(" ")
            # if parsed[1] == 'melee':
            #     melee = True
            #     stripped = [strip(word) for word in parsed[2:]]
            # else:
            #     stripped = [strip(word) for word in parsed[1:]]
            # search = "+".join(stripped)
            # try:
            #     scope_str = parsed[0][4:]
            #     scope = int(scope_str)
            #     if melee:
            #         num_gifs = scope
            # except:
            #     pass
            # choice = random.randint(1, scope)
            # response = requests.get(f"https://api.giphy.com/v1/gifs/search?q={search}&api_key=WiLstLIo2SInusTmGDDkhhY0tU6xKNEl&limit={num_gifs}&offset={choice}")
            # if response.status_code != 200:
            #     await message.channel.send("U stupid bruh, bad request.")
            # else:
            #     gifs = response.json()['data']
            #     gif_urls = [gif['url'] for gif in gifs]
            #     for url in gif_urls:
            #           message.channel.send(url)

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



if __name__ == "__main__":
    '''local resource loads'''
    # load paywalled sites
    paywalled_sites = load_paywalls()
    # load bot token
    token = load_token()

    '''bot instantiation'''
    # creates discord bot object (with member intents enabled to grab members)
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents = intents, command_prefix = '!', case_insensitive = True)
    #add command cogs to bot
    bot.add_cog(Archivist(paywalled_sites)) #archive is commands and listener 
    bot.add_cog(RateLimiter()) #gripe at sal and aj when they fight
    bot.add_cog(Utes()) #calc and gif
    bot.add_cog(Creeper(bot)) #listen to say weird things
    #run the bot
    bot.run(token)