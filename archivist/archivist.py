import discord
from discord.ext import commands
from utils import load_paywalls, load_token
from librarian import Librarian
from rando import Creeper, Utes, RateLimiter
from wordle import Wordle
from collector import Collector


if __name__ == "__main__":
    """local resource loads"""
    # load paywalled sites
    paywalled_sites = load_paywalls()
    # load bot token
    token = load_token()

    """bot instantiation"""
    # creates discord bot object (with member intents enabled to grab members)
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(intents=intents, command_prefix="!", case_insensitive=True)
    # add command cogs to bot
    bot.add_cog(Librarian(paywalled_sites))  # archive is commands and listener
    bot.add_cog(RateLimiter())  # gripe at sal and aj when they fight
    bot.add_cog(Utes())  # calc and gif
    bot.add_cog(Creeper(bot))  # listen to say weird things
    bot.add_cog(Wordle(bot))  # calculate wordle stats
    bot.add_cog(Collector(bot))  # aggregate yee data
    # run the bot
    bot.run(token)
