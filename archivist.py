import discord

with open("./token", "r") as file:
    token = file.read()

client = discord.Client()

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('!paywall'):
        msg = message.content.split(" ")[1]
        await client.send_message(message.channel, msg)
