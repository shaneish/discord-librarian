import discord
from discord.ext import commands
from utils import cprint, url_validator
import tldextract


class Librarian(commands.Cog):
    def __init__(self, paywalled_sites):
        self.paywalled_sites = paywalled_sites

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

    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks if message is a valid URL and a paywalled domain.  If it is, returns the archive.is link.
        if url_validator(message.content):
            raw_url = message.content
            url = tldextract.extract(message.content)
            if url.domain in self.paywalled_sites:
                await message.channel.send(f"https://www.archive.is/{raw_url}")