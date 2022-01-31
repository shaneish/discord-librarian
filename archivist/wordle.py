import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from statistics import median, stdev
import re


class Wordle(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command(name='score')
    async def score(self, message, *args):
        if len(args) > 0:
            if args[0].isdigit():
                wordle_str = f"Wordle {args[0]} (\d*X*)/6"
                user_name = None # TODO: implement user name search
            else:
                wordle_str = f"Wordle [0-9]+ (\d*X*)/6"
                user_name = args[0] # TODO: implement user name search
        else:
            wordle_str = f"Wordle [0-9]+ (\d*X*)/6"
            user_name = None # TODO: implement user name search
        collected_scores = list()
        async for msg in message.channel.history(limit=None):
            wordle_score = re.findall(wordle_str, msg.content)
            if len(wordle_score) > 0:
                n_score = 7 if ("X" in wordle_score[0]) else int(wordle_score[0])
                collected_scores.append(n_score)
        if len(collected_scores) > 0:
            plt.hist(collected_scores, bins=[1, 2, 3, 4, 5, 6, 7])
            plt.savefig("recent_wordle_plot.png")
            plt.clf()
            stats_msg = f"**Mean:** {sum(collected_scores)/len(collected_scores)}\n**Median:** {median(collected_scores)}\n**Std:** {stdev(collected_scores)}"
            await message.channel.send(stats_msg, file=discord.File("recent_wordle_plot.png"))
        else:
            await message.channel.send("No wordles found.")
