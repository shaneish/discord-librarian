import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from utils import load_token
import csv
import os


class Spy(commands.Cog):

    @commands.Cog.listener()
    async def on_message(self, message):
        with open(r"./data/discord_messages.csv", "a", newline='') as messages_csv:
            csv_file = csv.DictWriter(messages_csv, fieldnames=["Message", "Time", "Author", "Channel"])
            csv_file.writerow({'Message': message.content, 'Time': message.created_at, 'Author': message.author.name, 'Channel': message.channel})

class Collector(commands.Cog):

    @commands.command(name="collect")
    async def collect(self, message, *args):
        if len(args) > 0:
            if args[0].isdigit():
                num_messages = int(args[0])
        else:
            num_messages = None
        with open(f"./data/{message.channel}.csv", 'w') as data_file:
            writer = csv.DictWriter(data_file, fieldnames=["Message", "Time", "Author", "Channel"])
            writer.writeheader()
            async for msg in message.channel.history(limit=num_messages):
                writer.writerow({'Message': msg.content, 'Time': msg.created_at, 'Author': msg.author.name, 'Channel': message.channel})
        await message.channel.send(file=discord.File(f"./data/{message.channel}.csv"))
        os.remove(f"./data/{message.channel}.csv")

if __name__ == "__main__":
    '''local resource loads'''
    # load bot token
    token = load_token()

    '''bot instantiation'''
    # creates discord bot object (with member intents enabled to grab members)
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents=intents, command_prefix='!', case_insensitive=True)
    #add command cogs to bot
    bot.add_cog(Spy())
    bot.add_cog(Collector())
    #run the bot
    bot.run(token)