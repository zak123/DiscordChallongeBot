import discord
from discord.ext import commands
from challonge_helper import *
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=config['Options']['command_prefix'], intents=intents)

current_challonge_id = 0
current_challonge_url = 'http://challonge.com'
monitor_enabled = False


@bot.command()
async def set(ctx, arg):
    if ctx.message.author.guild_permissions.administrator:
        try:
            global current_challonge_id
            global current_challonge_url
            info = await GetTournament(arg)
            current_challonge_id = info['id']
            current_challonge_url = info['full_challonge_url']
            await ctx.send(f"**{info['name']}** has been set as the current tournament")
        except Exception as err:
            await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")
    else:
        await ctx.send(config['ErrorMessages']['permission_error_admin'])


@bot.command()
async def status(ctx):
    if current_challonge_id == 0:
        return await ctx.send('Please set a tournament with $set url/id')
    try:
        matches = await GetMatches(current_challonge_id)
        return await update_tournament_status_discord(ctx, matches)
    except Exception as err:
        await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


async def monitor_loop(ctx):
    matches = []

    while monitor_enabled:
        matches_new = await GetMatches(current_challonge_id)

        if matches != matches_new:
            await update_tournament_status_discord(ctx, matches_new)
            matches = matches_new

        await asyncio.sleep(15)


@bot.command()
async def monitor(ctx):
    if ctx.message.author.guild_permissions.administrator:
        if current_challonge_id == 0:
            return await ctx.send('Please set a tournament with $set url/id')

        try:
            global monitor_enabled
            monitor_enabled = True
            await ctx.send('**__Now monitoring the current tournament. Immediately play any matches that are listed here!__**')
            await monitor_loop(ctx)
        except Exception as err:
            await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")

    else:
        await ctx.send(config['ErrorMessages']['permission_error_admin'])


@bot.command()
async def stop(ctx):
    if ctx.message.author.guild_permissions.administrator:
        global monitor_enabled
        monitor_enabled = False
        await ctx.send('No longer monitoring the current tournament. Use $monitor to enable tournament monitoring.')
    else:
        await ctx.send(config['ErrorMessages']['permission_error_admin'])


# @bot.command()
# async def report(ctx, arg1, arg2):
#     try:
#         response = await ReportMatch(current_challonge_id, arg1, arg2)
#         print(response)
#     except Exception as err:
#         await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


# Reusable function that takes in the current matches and spits out upcoming/current matches for discord
async def update_tournament_status_discord(ctx, matches):
    try:
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
                                                value=f"{match['round_string']}\n{match['id']}", inline=True)
            if match['state'] == 'pending':
                if match.get('player1_name') != None or match.get('player2_name') != None:
                    num_upcoming += 1
                    upcoming_matches_embed.add_field(name=player_vs_string,
                                                     value=f"{match['round_string']}\n{match['id']}", inline=True)
        if num_current > 0:
            await ctx.send("**Update!**", embed=current_matches_embed)

        if num_upcoming > 0 and config['Options'].getboolean('show_upcoming_matches'):
            await ctx.send(embed=upcoming_matches_embed)

        if num_current == 0 & num_upcoming == 0:
            info = await GetTournament(current_challonge_id)

            if info['state'] == 'awaiting_review' or info['state'] == 'complete':
                if info['state'] == 'awaiting_review' and config['Options'].getboolean('auto_finalize_tournament_after_grand_finals'):
                    await EndTournament(current_challonge_id)
                else:
                    return await ctx.send('Please finalize the tournament by clicking "End the tournament" on challonge, tournamentor will display results once finalized.')

                results = await GetParticipants(current_challonge_id)
                results.sort(key=lambda x: x['final_rank'], reverse=False)
                results_message = 'The tournament is over! Thank you for playing!\n```'
                for result in results:
                    results_message += f"#{result['final_rank']} - {result['name']}\n"

                await ctx.send(f"{results_message}```\nStopping monitoring for this tournament. Congratulations to the winner!")
                global monitor_enabled
                monitor_enabled = False
            else:
                await ctx.send('No matches for this tournament')
    except Exception as err:
        await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


bot.run(config['Tokens']['discord_api_key'])
