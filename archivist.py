import discord
import asyncio

with open("./token", "r") as file:
    token = file.read()

client = discord.Client()

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('!paywall'):
        msg = message.content.split(" ")[1]
        await message.channel.send(message.channel, msg)

client.run(token)