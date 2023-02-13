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
    matches = {}

    while monitor_enabled:
        matches_new = await GetMatches(current_challonge_id)
        # open_matches_new = matches_new.get('open_matches')
        # open_matches_old = matches.get('open_matches')

        # upcoming_matches_new = matches_new.get('upcoming_matches')
        # upcoming_matches_old = matches.get('upcoming_matches')

        # stream_matches_new = matches_new.get('stream_matches')
        # stream_matches_old = matches.get('stream_matches')

        # if config['Options'].getboolean('only_show_new_matches_while_monitoring'):
        #     if matches != matches_new:
        #         if open_matches_new != None and open_matches_old != None:
        #             for match in open_matches_old:
        #                 for match_new in open_matches_new:
        #                     if match_new['id'] == match['id']:
        #                         open_matches_new.remove(match_new)
                # if matches_new.get('upcoming_matches') != None and matches.get('upcoming_matches') != None:
                #     matches_new['upcoming_matches'] = matches.get(
                #         'upcoming_matches') - matches_new.get('upcoming_matches')

                # if matches_new.get('stream_matches') != None and matches.get('stream_matches') != None:
                #     matches_new['stream_matches'] = matches.get(
                #         'stream_matches') - matches_new.get('stream_matches')
        # print(matches_new)
        if config['Options'].getboolean('show_upcoming_matches_while_monitoring'):
            if matches != matches_new:
                await update_tournament_status_discord(ctx, matches_new)
                matches = matches_new
        else:
            if matches.get('open_matches') != matches_new.get('open_matches'):
                await update_tournament_status_discord(ctx, matches_new, False)
                matches = matches_new

        await asyncio.sleep(config['Options'].getfloat('monitor_refresh_interval'))


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
async def update_tournament_status_discord(ctx, matches, show_upcoming_matches=True):
    # try:
    if (matches != None):
        stream_matches_embed = discord.Embed(
            title="Stream Match", url=current_challonge_url, description="Wait for a TO to coordinate this match!")
        current_matches_embed = discord.Embed(title="Current Matches", url=current_challonge_url,
                                              description="Please play these matches as soon as possible!")
        upcoming_matches_embed = discord.Embed(
            title="Upcoming Matches", url=current_challonge_url, description="These are on deck matches, be ready to play!")

        if len(matches.get('stream_matches')) > 0:
            for stream_match in matches.get('stream_matches'):
                print(stream_match)
                stream_matches_embed.add_field(
                    name=stream_match['player_vs_string'], value=stream_match['round_string'], inline=True)
            await ctx.send(embed=stream_matches_embed)

        if len(matches.get('open_matches')) > 0:
            for open_match in matches.get('open_matches'):
                current_matches_embed.add_field(name=open_match['player_vs_string'],
                                                value=open_match['round_string'], inline=True)
            await ctx.send(embed=current_matches_embed)

        if len(matches.get('upcoming_matches')) > 0 and config['Options'].getboolean('show_upcoming_matches') and show_upcoming_matches:
            for upcoming_match in matches.get('upcoming_matches'):
                upcoming_matches_embed.add_field(name=upcoming_match['player_vs_string'],
                                                 value=upcoming_match['round_string'], inline=True)
            await ctx.send(embed=upcoming_matches_embed)

        if len(matches.get('open_matches')) == 0 and len(matches.get('upcoming_matches')) == 0 and len(matches.get('stream_matches')) == 0:
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
    else:
        await ctx.send('Please start the tournament!')

    # except Exception as err:
    #     await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


bot.run(config['Tokens']['discord_api_key'])
