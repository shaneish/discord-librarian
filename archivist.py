import discord
import asyncio

with open("./token", "r") as file:
    token = file.read()

client = discord.Client()

@client.event
async def on_message(message):

    if message.content.startswith('!paywall'):
        words = message.content.split(" ")
        await message.channel.send(f"https://www.archive.is/{words[1]}")

    if message.content.startswith('who is a horrible person?'):
        await message.channel.send(f"Why, @Sal of course!")

client.run(token)