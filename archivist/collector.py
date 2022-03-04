import discord
from discord.ext import commands
import csv
import os
import pathlib
from datetime import datetime


class Collector(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(name="collect")
    async def collect(self, message, *args):
        num_messages = None
        f = (
            pathlib.Path(__file__).parent
            / "resources"
            / f"{message.channel}-{datetime.now().strftime('%Y%m-%d%H-%M%S-')}.csv"
        )
        if len(args) > 0:
            if args[0].isdigit():
                num_messages = int(args[0])
        with open(f, "w") as data_file:
            writer = csv.DictWriter(
                data_file, fieldnames=["Message", "Time", "Author", "Channel"]
            )
            writer.writeheader()
            async for msg in message.channel.history(limit=num_messages):
                writer.writerow(
                    {
                        "Message": msg.content,
                        "Time": msg.created_at,
                        "Author": msg.author.name,
                        "Channel": message.channel,
                    }
                )
        await message.channel.send(file=discord.File(f))
        os.remove(f)

    @commands.command(name="collect_all")
    async def collect_all(self, ctx, *args):
        num_messages = None
        f = (
            pathlib.Path(__file__).parent
            / "resources"
            / f"all_messages-{datetime.now().strftime('%Y%m-%d%H-%M%S-')}.csv"
        )
        if len(args) > 0:
            if args[0].isdigit():
                num_messages = int(args[0])
        total_channels = len(ctx.guild.text_channels)
        with open(f, "w") as data:
            writer = csv.DictWriter(
                data, fieldnames=["Message", "Time", "Author", "Channel"]
            )
            writer.writeheader()
            scrape_pct = await ctx.send("Scraping complete: 0.00%")
            for index, channel in enumerate(ctx.guild.text_channels):
                try:
                    async for msg in channel.history(limit=num_messages):
                        writer.writerow(
                            {
                                "Message": msg.content,
                                "Time": msg.created_at,
                                "Author": msg.author.name,
                                "Channel": msg.channel,
                            }
                        )
                except:
                    pass
                await scrape_pct.edit(
                    content=f"Scraping complete: {round((index+1)*100/total_channels, 2)}%"
                )
            await ctx.channel.send(file=discord.File(f))
        os.rename(
            f, pathlib.Path(__file__).parent / "resources" / "server_messages.csv"
        )
