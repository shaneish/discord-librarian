import discord
import asyncio
import tldextract
from urllib.parse import urlparse

def url_validator(x):
    '''
    Quick function to validate if 'x' is a proper URL or not

    Returns: Boolean
    '''
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

# read the paywalled config file to read all websites currently redirected by TheLibrarian
with open('paywalled', 'r') as file:
    paywalled_sites = file.read().split("\n")

# read TheLibrarians Discord token
with open("./token", "r") as file:
    token = file.read()

# creates discord Client object
client = discord.Client()

# all responses triggered by a message are thrown in here
@client.event
async def on_message(message):
    global paywalled_sites # include list of paywalled site inside this function

    if message.content.startswith('!paywall'):
        '''
        Manually link to archive.is

        Format: `!paywall URL` will link to archive.is/URL
        '''
        words = message.content.split(" ")
        await message.channel.send(f"https://www.archive.is/{words[1]}")

    if ('thank' in message.content.lower()) and ('soros' in message.content.lower()):
        '''
        Responds to Sal when he says 'Thanks Soros'

        (note: not antisemitic joke, used to mock the antisemitic globalist Soros stories)
        '''
        await message.channel.send('No problemo buckaroo, anything for a fellow reptile.')

    if ('who' in message.content.lower()) and ('horrible' in message.content.lower()):
        '''
        You know what this does
        '''
        await message.channel.send(f"Why, {message.author} of course!")

    if url_validator(message.content):
        '''
        Checks if message is a valid URL and a paywalled domain.  If it is, returns the archive.is link.
        '''
        raw_url = message.content
        url = tldextract.extract(message.content)
        if url.domain in paywalled_sites:
            await message.channel.send(f"https://www.archive.is/{raw_url}")
    
    if message.content.startswith('!add'):
        '''
        Add new domains to list of paywalled domains

        Format: `!add DOMAIN_1 DOMAIN_2 ... DOMAIN_n` will add DOMAIN_1 thru DOMAIN_n to list
            of paywalled sites and respond with a confirmation message.
        '''
        new_paywalls = message.content.split(" ")[1:]
        paywalled_sites += new_paywalls 
        with open('paywalled', 'a') as file:
            sites = "\n" + "\n".join(new_paywalls)
            file.write(sites)
            await message.channel.send('Added the following domains:' + sites)
    
    if message.content.startswith("!list paywalls"):
        '''
        Displays list of all sites on the current paywall list
        '''
        await message.channel.send("\n".join(sorted(paywalled_sites)))

if __name__ == "__main__":
    client.run(token)