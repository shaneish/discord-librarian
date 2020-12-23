import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from utils import load_token, team_schedule, gen_leaderboard, nfl_map, split_df, cprint_df


class Requests(commands.Cog):

    @commands.command(name="schedule")
    async def schedule(self, message, *args):
        if len(args) > 0:
            await message.channel.send(team_schedule(" ".join(args)))
        else:
            await message.channel.send("**You idjot, plz include a team to query.")
    
    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx, *args):
        teams = " ".join(args).split("/")
        if (len(teams) > 0) and (teams[0] != ''):
            leaderboard = gen_leaderboard(name_map=nfl_map, teams=teams)
            for chunk in split_df(leaderboard):
                await ctx.send(cprint_df(chunk))
        else:
            leaderboard = gen_leaderboard(name_map=nfl_map, teams=nfl_map.keys())
            for chunk in split_df(leaderboard):
                await ctx.send(cprint_df(chunk))

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
    bot.add_cog(Requests())
    #run the bot
    bot.run(token)