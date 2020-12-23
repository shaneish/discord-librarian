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
        with open(r"./data/server_messages.csv", "a", newline='') as messages_csv:
            csv_file = csv.DictWriter(messages_csv, fieldnames=["Message", "Time", "Author", "Channel"])
            csv_file.writerow({'Message': message.content, 'Time': message.created_at, 'Author': message.author.name, 'Channel': message.channel})

class Collector(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="collect")
    async def collect(self, message, *args):
        num_messages = None
        if len(args) > 0:
            if args[0].isdigit():
                num_messages = int(args[0])
        with open(f"./data/{message.channel}.csv", 'w') as data_file:
            writer = csv.DictWriter(data_file, fieldnames=["Message", "Time", "Author", "Channel"])
            writer.writeheader()
            async for msg in message.channel.history(limit=num_messages):
                writer.writerow({'Message': msg.content, 'Time': msg.created_at, 'Author': msg.author.name, 'Channel': message.channel})
        await message.channel.send(file=discord.File(f"./data/{message.channel}.csv"))
        os.remove(f"./data/{message.channel}.csv")
    
    @commands.command(name="collect_all")
    async def collect_all(self, ctx, *args):
        num_messages = None
        if len(args) > 0:
            if args[0].isdigit():
                num_messages = int(args[0])
        total_channels = len(ctx.guild.text_channels)
        with open("./data/temp.csv", "w") as data:
            writer = csv.DictWriter(data, fieldnames=["Message", "Time", "Author", "Channel"])
            writer.writeheader()
            scrape_pct = await ctx.send("Scraping complete: 0.00%")
            for index, channel in enumerate(ctx.guild.text_channels):
                try:
                    async for msg in channel.history(limit=num_messages):
                        writer.writerow({'Message': msg.content, 'Time': msg.created_at, 'Author': msg.author.name, 'Channel': msg.channel})
                except:
                    pass
                await scrape_pct.edit(content=f"Scraping complete: {round((index+1)*100/total_channels, 2)}%")
        os.rename("./data/temp.csv", "./data/server_messages.csv")

if __name__ == "__main__":
    '''local resource loads'''
    # load bot token
    token = load_token()
    # create client
    client = discord.Client()

    '''bot instantiation'''
    # creates discord bot object (with member intents enabled to grab members)
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents=intents, command_prefix='!', case_insensitive=True)
    #add command cogs to bot
    bot.add_cog(Spy())
    bot.add_cog(Collector(client))
    #run the bot
    bot.run(token)