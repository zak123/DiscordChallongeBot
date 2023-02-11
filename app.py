import discord
from discord.ext import commands
from challonge_helper import *


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
    matches = await GetOngoingMatches(arg)
    print(matches)

    embed = discord.Embed(title="Ongoing Matches", url="http://challonge.com",
                          description="Please play these matches as soon as possible!")
    for match in matches:
        embed.add_field(name=f"{match['player1_name']} vs {match['player2_name']}",
                        value=f"This is a Round {match['round']} match.", inline=False)

    await ctx.send(embed=embed)


def check_status_loop():
    return 0


bot.run('MTA3NDA3MzQ3ODAyNzgxMjg3NA.Gjq1oB.Zapy5zsrHiAWV0Jx1PNd6Zfjf6tW2ln1ABVPp4')
