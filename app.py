import discord
from discord.ext import commands
from challonge_helper import *
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

current_challonge_id = 0
current_challonge_url = 'http://challonge.com'


@bot.command()
async def set(ctx, arg):
    global current_challonge_id
    global current_challonge_url
    info = await GetTournament(arg)
    current_challonge_id = info['id']
    current_challonge_url = info['full_challonge_url']
    await ctx.send(f"**{info['name']}** has been set as the current tournament")


@bot.command()
async def status(ctx):
    if current_challonge_id == 0:
        return await ctx.send('Please set a tournament with $set url/id')

    matches = await GetMatches(current_challonge_id)
    return await update_tournament_status(ctx, matches)


async def monitor_loop(ctx):
    matches = []
    tournament_ongoing = True

    while tournament_ongoing:
        matches_new = await GetMatches(current_challonge_id)

        if matches != matches_new:
            await update_tournament_status(ctx, matches_new)
            matches = matches_new

        await asyncio.sleep(15)


@bot.command()
async def monitor(ctx):
    if current_challonge_id == 0:
        return await ctx.send('Please set a tournament with $set url/id')

    await ctx.send('**__Now monitoring the current tournament. Immediately play any matches that are listed here!__**')
    await monitor_loop(ctx)


async def update_tournament_status(ctx, matches):
    current_matches_embed = discord.Embed(title="Current Matches", url=current_challonge_url,
                                          description="Please play these matches as soon as possible!")
    upcoming_matches_embed = discord.Embed(
        title="Upcoming Matches", url=current_challonge_url, description="These are on deck matches, be ready to play!")

    num_current = 0
    num_upcoming = 0

    for match in matches:

        player_vs_string = f"{match.get('player1_name') if match.get('player1_name') else '???' } vs {match.get('player2_name') if match.get('player2_name') else '???'}"

        if match['state'] == 'open':
            num_current += 1
            current_matches_embed.add_field(name=player_vs_string,
                                            value=match['round_string'], inline=True)
        if match['state'] == 'pending':
            num_upcoming += 1
            if match.get('player1_name') != None or match.get('player2_name') != None:
                upcoming_matches_embed.add_field(name=player_vs_string,
                                                 value=match['round_string'], inline=True)
    if num_current > 0:
        await ctx.send("**Update!**", embed=current_matches_embed)
    if num_upcoming > 0:
        await ctx.send(embed=upcoming_matches_embed)
    if num_current == 0 & num_upcoming == 0:
        info = await GetTournament(current_challonge_id)
        if info['state'] == 'awaiting_review' or info['state'] == 'complete':
            await EndTournament(current_challonge_id)
            results = await GetParticipants(current_challonge_id)
            results.sort(key=lambda x: x['final_rank'], reverse=False)
            results_message = 'The tournament is over! Thank you for playing!\n```'
            for result in results:
                results_message += f"#{result['final_rank']} - {result['name']}\n"
            await ctx.send(f"{results_message}```")
        else:
            await ctx.send('No matches for this tournament')


bot.run('MTA3NDA3MzQ3ODAyNzgxMjg3NA.Gjq1oB.Zapy5zsrHiAWV0Jx1PNd6Zfjf6tW2ln1ABVPp4')
