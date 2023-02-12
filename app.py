import discord
from discord.ext import commands
from challonge_helper import *
import time


intents = discord.Intents.default()
intents.message_content = True

# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command()
async def get(ctx, arg):
    await ctx.send(await GetTournament(arg))


@bot.command()
async def start(ctx, arg):
    # await ctx.send(await StartTournament(arg))
    matches = []
    tournament_ongoing = True

    await ctx.send('**__The tournament is starting! Please pay attention to this channel. Immediately play any matches that are listed here.__**')

    while tournament_ongoing:
        matches_new = await GetOngoingMatches(arg)

        if matches != matches_new:
            embed = discord.Embed(title="New Ongoing Matches", url="http://challonge.com",
                                  description="Please play these matches as soon as possible!")
            for match in matches_new:
                if match['round'] > 0:
                    embed.add_field(name=f"{match['player1_name']} vs {match['player2_name']}",
                                    value=f"This is a round {match['round']} match.", inline=False)
                elif match['round'] < 0:
                    embed.add_field(name=f"{match['player1_name']} vs {match['player2_name']}",
                                    value=f"This is a losers round {match['round'] * -1} match.", inline=False)

            await ctx.send(embed=embed)

            matches = matches_new

        time.sleep(20)


bot.run('MTA3NDA3MzQ3ODAyNzgxMjg3NA.Gjq1oB.Zapy5zsrHiAWV0Jx1PNd6Zfjf6tW2ln1ABVPp4')
