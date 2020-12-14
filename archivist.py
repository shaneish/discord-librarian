import discord
import asyncio
import tldextract
from urllib.parse import urlparse

def url_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

with open('paywalled', 'r') as file:
    paywalled_sites = file.read().split("\n")

with open("./token", "r") as file:
    token = file.read()

client = discord.Client()

@client.event
async def on_message(message):
    global paywalled_sites

    if message.content.startswith('!paywall'):
        words = message.content.split(" ")
        await message.channel.send(f"https://www.archive.is/{words[1]}")

    if ('thank' in message.content.lower()) and ('soros' in message.content.lower()):
        await message.channel.send('No problemo buckaroo, anything for a fellow reptile.')

    if message.content.startswith('who is a horrible person?'):
        await message.channel.send(f"Why, {message.author} of course!")

    if url_validator(message.content):
        raw_url = message.content
        url = tldextract.extract(message.content)
        if url.domain in paywalled_sites:
            await message.channel.send(f"https://www.archive.is/{raw_url}")
    
    if message.content.startswith('!add'):
        new_paywalls = message.content.split(" ")[1:]
        paywalled_sites += new_paywalls 
        with open('paywalled', 'a') as file:
            sites = "\n" + "\n".join(new_paywalls)
            file.write(sites)
            await message.channel.send('Add the following domains:' + sites)
    
    if message.content.startswith("!list paywalls"):
        await message.channel.send("\n".join(paywalled_sites))

if __name__ == "__main__":
    client.run(token)