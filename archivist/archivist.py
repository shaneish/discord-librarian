import discord
from discord.ext import commands 
import asyncio
import tldextract
import requests
from utils import cprint, url_validator, load_paywalls, load_token, and_includes, or_includes, strip, MalarkyDict, load_malarkey, save_malarkey
import random
from datetime import datetime, timedelta
import pickle
import sys


class Archivist(commands.Cog):
    def __init__(self, paywalled_sites, malarkey_dict):
        self.paywalled_sites = paywalled_sites
        self.malarkey_dict = malarkey_dict

    @commands.command(name='paywalls')
    async def paywalls(self, ctx, *args):
        if args[0] == 'add':
            # Add new domains to list of paywalled domains
            # Format: `!paywalls add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
            #     of paywalled sites and respond with a confirmation message.
            self.paywalled_sites = list(set(self.paywalled_sites).union(set(args[1:])))
            with open('paywalled', 'w') as file:
                sites = "\n".join(self.paywalled_sites)
                file.write(sites)
                await ctx.send('**Added the following domains:**' + "\n" + cprint(args[1:]))
        elif args[0] == 'list':
            # List all paywalled sites currently tracking
            # Format: `!paywalls list` will list all paywalled sites
            await ctx.send("**Paywalled sites:**" + "\n" + cprint(sorted(self.paywalled_sites)))
        elif args[0] == 'delete':
            # Delete domains to list of paywalled domains
            # Format: `!paywalls delete DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
            #     of paywalled sites and respond with a confirmation message.
            self.paywalled_sites = list(set(self.paywalled_sites).difference(set(args[1:])))
            with open('paywalled', 'w') as file:
                sites = "\n".join(self.paywalled_sites)
                file.write(sites)
                await ctx.send('**Deleted the following domains:**' + "\n" + cprint(args[1:]))
        elif args[0] == 'link':
            # Manually link to archive.is
            # Format: `!paywalls link URL` will link to archive.is/URL
            if url_validator([args[1]]):
                await ctx.send(f"https://www.archive.is/{args[1]}")
            else:
                await ctx.send(f"**{args[1]}** is an invalid url.")
        
    @commands.command(name="malarkey")
    async def malarkey(self, ctx, *args):
        # implementation of the malarkey meter
        if "sal" not in ctx.message.author.name.lower():
            if (len(args) > 1) and (args[0].isdigit()):
                # if first arg is a positive integer, create/update the group represented by the subsequent words
                words = set(args[1:])
                try:
                    self.malarkey_dict[words] = int(args[0])
                    save_malarkey(self.malarkey_dict)
                    await ctx.send(f"New malarkey group {words} with value {int(args[0])} added!")
                except ValueError:
                    await ctx.send("Incompatible malarkey addition, stupid.")
            elif (len(args) == 0) or ((len(args) == 1) and (args[0] == "")):
                # if just !malarkey by itself is called, calculate the malarkey meter for the last 30 mins and send a chat update
                # with the current malarkey level
                malarkey_count = 0
                for message in await ctx.channel.history(limit=1000, after=ctx.message.created_at - timedelta(minutes=30)).flatten():
                    if message.content:
                        malarkey_count += self.malarkey_dict.measure_malarkey(message.content)
                if malarkey_count < 1:
                    await ctx.send("**No Malarkey detected.**")
                elif malarkey_count < 200:
                    await ctx.send("**Minimal Malarkey**")
                elif malarkey_count < 400:
                    await ctx.send("**Potential Malarkey**")
                elif malarkey_count < 600:
                    await ctx.send("**Significant Malarkey**")
                elif malarkey_count < 800:
                    await ctx.send("**Extreme levels of Malarkey**")
                elif malarkey_count < 1000:
                    await ctx.send("**:rotating_light: Malarkey Quarantine :rotating_light:**")
                else:
                    await ctx.send("**:fire: :fire: GET OUTTA HERE, JACK! :fire: :fire:**")
            elif args[0] == "groups":
                # if first arg is 'groups', list all of the group representations and their corresponding malarkey levels
                await ctx.send('```' + str(self.malarkey_dict)[1:-1] + '```')
            elif args[0] == 'update':
                # if the first arg is 'update', find the group representation of the second arg and 
                # add all subsequent args to that group representation
                try:
                    self.malarkey_dict._update_key(args[1:])
                    save_malarkey(self.malarkey_dict)
                    await ctx.send(f"Added {set(args[2:])} to {args[1]}'s group.")
                except ValueError:
                    await ctx.send("Incompatible group addition, dummy.")
            # need to fix remove feature below.  Currently a catastrophic failure that removes entire MalarkeyDict
            '''
            elif args[0] == "remove":
                try:
                    self.malarkey_dict.remove_from_group(args[1])
                    save_malarkey(self.malarkey_dict)
                    await ctx.send(f"Removed {args[1]} from group.")
                except ValueError:
                    await ctx.send("Unable to remove from a group.")
            '''

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

class Creeper(commands.Cog):
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



if __name__ == "__main__":
    '''local resource loads'''
    # load paywalled sites
    paywalled_sites = load_paywalls()
    # load bot token
    token = load_token()
    # load malarkeydict
    malarkey = load_malarkey()

    '''bot instantiation'''
    # creates discord bot object (with member intents enabled to grab members)
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents = intents, command_prefix = '!', case_insensitive = True)
    #add command cogs to bot
    bot.add_cog(Archivist(paywalled_sites, malarkey)) #archive is commands and listener 
    bot.add_cog(RateLimiter()) #gripe at sal and aj when they fight
    bot.add_cog(Utes()) #calc and gif
    bot.add_cog(Creeper(bot)) #listen to say weird things
    #run the bot
    bot.run(token)