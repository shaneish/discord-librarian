import discord
from discord import *
import asyncio
import tldextract
import requests
import json
from urllib.parse import urlparse
from utils import cprint, url_validator, load_paywalls, load_token, and_includes, or_includes, strip
import random
from ast import literal_eval
from datetime import datetime, timedelta

# load paywalled sites
paywalled_sites = load_paywalls()

# load bot token
token = load_token()

# creates discord Client object
client = discord.Client()

#check last rate limiter check in time
last_check_in = None

# all responses triggered by a message are thrown in here
@client.event
async def on_message(message: Message):
    
    

    global paywalled_sites # include list of paywalled site inside this function
    global last_check_in
    
    #rate limiter
    if message.content.startswith('!test'):
        #TODO: Put some random fuzz on the checkin timedelta
        #TODO: Lower the checkin time delta based on the subsequent frequency
        if not last_check_in or  last_check_in < (message.created_at - timedelta(seconds = 60)):
            #grab the bot ids
            memb_ls=[m async for m in message.guild.fetch_members(limit=None) if not m.bot]
            #grab the last ten minutes of messages, up to 200 messages
            last_check_in = message.created_at
            ten_min_ago = message.created_at - timedelta(seconds = 600)
            messages = await message.channel.history(limit = 600, after = ten_min_ago).flatten()
            #get the history of message authors who aren't bots
            human_authors_history = [m.author for m in messages if m.author in memb_ls] #hopefully member objects are singleton across calls, else rework on ids
            #get the unique authors
            human_author_set = set(human_authors_history)
            if len(human_author_set) == 2:
                prefix = f"{list(human_author_set)[0].mention} and {list(human_author_set)[1].mention} are "
            elif len(human_author_set) == 1:
                prefix = f"{list(human_author_set)[0].mention} is "

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

    if message.content.startswith('!paywall'):
        # Manually link to archive.is
        # Format: `!paywall URL` will link to archive.is/URL
        words = message.content.split(" ")
        await message.channel.send(f"https://www.archive.is/{words[1]}")

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
    
    if or_includes(message.content, 'shane', 'metricity', 'the best')  and (message.author != client.user):
        await message.channel.send(f"Shane really is the best.")
    
    if or_includes(message.content, "suck", "sux") and (message.author != client.user):
        # ya know what this does too
        await message.channel.send("You know what else sucks? Salex Bexman.")

    if url_validator(message.content):
        # Checks if message is a valid URL and a paywalled domain.  If it is, returns the archive.is link.
        raw_url = message.content
        url = tldextract.extract(message.content)
        if url.domain in paywalled_sites:
            await message.channel.send(f"https://www.archive.is/{raw_url}")
    
    if message.content.startswith('!add'):
        # Add new domains to list of paywalled domains
        # Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
        #     of paywalled sites and respond with a confirmation message.
        new_paywalls = message.content.split(" ")[1:]
        paywalled_sites += new_paywalls
        paywalled_sites = list(set(paywalled_sites))
        paywalled_sites = [i for i in paywalled_sites if i != ""]
        with open('paywalled', 'w') as file:
            sites = "\n".join(paywalled_sites)
            file.write(sites)
            await message.channel.send('**Added the following domains:**' + "\n" + cprint(new_paywalls))

    if message.content.startswith('!delete'):
        # Delete domains to list of paywalled domains
        # Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
        #     of paywalled sites and respond with a confirmation message.
        new_paywalls = message.content.split(" ")[1:]
        paywalled_sites = [i for i in paywalled_sites if i not in new_paywalls]
        with open('paywalled', 'w') as file:
            sites = "\n".join(paywalled_sites)
            file.write(sites)
            await message.channel.send('**Deleted the following domains:**' + "\n" + cprint(new_paywalls))
    
    if message.content.startswith("!list paywalls"):
        # Displays list of all sites on the current paywall list
        await message.channel.send("**Paywalled sites:**" + "\n" + cprint(sorted(paywalled_sites)))
    
    if message.content.startswith("!test"):
        await message.channel.send("Stop spamming the fucking chat with your damn tests u chode.")
        
    if message.content.startswith("!gif"):
        async with message.channel.typing(): #makes the channel say the bot is typing
            scope = 1
            melee = False
            num_gifs = 1
            parsed = message.content.split(" ")
            if parsed[1] == 'melee':
                melee = True
                stripped = [strip(word) for word in parsed[2:]]
            else:
                stripped = [strip(word) for word in parsed[1:]]
            search = "+".join(stripped)
            try:
                scope_str = parsed[0][4:]
                scope = int(scope_str)
                if melee:
                    num_gifs = scope
            except:
                pass
            choice = random.randint(1, scope)
            response = requests.get(f"https://api.giphy.com/v1/gifs/search?q={search}&api_key=WiLstLIo2SInusTmGDDkhhY0tU6xKNEl&limit={num_gifs}&offset={choice}")
            if response.status_code != 200:
                await message.channel.send("U stupid bruh, bad request.")
            else:
                gifs = response.json()['data']
                gif_urls = [gif['url'] for gif in gifs]
                for url in gif_urls:
                    await message.channel.send(url)

    if message.content.startswith("!calc"):
        async with message.channel.typing(): #makes the channel say the bot is typing
            terms = " ".join(message.content.split(" ")[1:])
            await message.channel.send(eval(terms))

if __name__ == "__main__":
    client.run(token)