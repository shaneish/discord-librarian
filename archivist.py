import discord
import asyncio
import tldextract
from urllib.parse import urlparse
from utils import cprint, url_validator, load_paywalls, load_token, and_includes, or_includes

# load paywalled sites
paywalled_sites = load_paywalls()

# load bot token
token = load_token()

# creates discord Client object
client = discord.Client()

# all responses triggered by a message are thrown in here
@client.event
async def on_message(message):
    global paywalled_sites # include list of paywalled site inside this function

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
        await message.channel.send(f"Why, {message.author} of course!")
    
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
            await message.channel.send('**Added the following domains:**' + "\n" + cprint(new_paywalls, sep=" - "))

    if message.content.startswith('!delete'):
        # Delete domains to list of paywalled domains
        # Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
        #     of paywalled sites and respond with a confirmation message.
        new_paywalls = message.content.split(" ")[1:]
        paywalled_sites = [i for i in paywalled_sites if i not in new_paywalls]
        with open('paywalled', 'w') as file:
            sites = "\n".join(paywalled_sites)
            file.write(sites)
            await message.channel.send('**Deleted the following domains:**' + "\n" + cprint(new_paywalls, sep=" - "))
    
    if message.content.startswith("!list paywalls"):
        # Displays list of all sites on the current paywall list
        await message.channel.send("**Paywalled sites:**" + "\n" + cprint(sorted(paywalled_sites), sep=" - "))

if __name__ == "__main__":
    client.run(token)