import discord
from discord.ext import commands
from challonge_helper import *
import asyncio
import configparser
import formatting_helper

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

        open_matches = matches.get('open_matches')
        upcoming_matches = matches.get('upcoming_matches')
        stream_matches = matches.get('stream_matches')

        await update_tournament_status_discord_new(ctx, open_matches, "Current Matches", config['Strings']['current_matches_text'])
        await update_tournament_status_discord_new(ctx, upcoming_matches, "Upcoming Matches", config['Strings']['upcoming_matches_text'])
        await update_tournament_status_discord_new(ctx, stream_matches, "Stream Matches", config['Strings']['stream_matches_text'])
        return
    except Exception as err:
        await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


async def monitor_loop(ctx):
    matches = {}

    while monitor_enabled:
        matches_new = await GetMatches(current_challonge_id)

        open_matches_new = matches_new.get('open_matches')
        open_matches_old = matches.get('open_matches')

        upcoming_matches_new = matches_new.get('upcoming_matches')
        upcoming_matches_old = matches.get('upcoming_matches')

        stream_matches_new = matches_new.get('stream_matches')
        stream_matches_old = matches.get('stream_matches')
        if open_matches_new != None:
            print("new", len(open_matches_new))
        if open_matches_old != None:
            print("old", len(open_matches_old))

        if config['Options'].getboolean('only_show_new_matches_while_monitoring'):
            if open_matches_new != open_matches_old:
                if open_matches_new != None and open_matches_old != None:
                    open_matches_differences = formatting_helper.find_differences(
                        open_matches_new, open_matches_old)
                    if len(open_matches_differences) > 0:
                        await update_tournament_status_discord_new(ctx, open_matches_differences, "NEW Current Matches", config['Strings']['current_matches_text'])
            if config['Options'].getboolean('show_upcoming_matches_while_monitoring'):
                if upcoming_matches_new != upcoming_matches_old:
                    if upcoming_matches_new != None and upcoming_matches_old != None:
                        upcoming_matches_differences = formatting_helper.find_differences(
                            upcoming_matches_new, upcoming_matches_old)
                        if len(upcoming_matches_differences) > 0:
                            await update_tournament_status_discord_new(ctx, upcoming_matches_differences, "NEW Upcoming Matches", config['Strings']['upcoming_matches_text'])
            if stream_matches_new != stream_matches_old:
                if stream_matches_new != None and stream_matches_old != None:
                    stream_matches_differences = formatting_helper.find_differences(
                        stream_matches_new, stream_matches_old)
                    if len(stream_matches_differences) > 0:
                        await update_tournament_status_discord_new(ctx, stream_matches_differences, "NEW Stream Matches", config['Strings']['stream_matches_text'])

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


async def update_tournament_status_discord_new(ctx, matches, match_category, match_description):
    if (len(matches) > 0):
        # continue
        embed = discord.Embed(
            title=match_category, url=current_challonge_url, description=match_description
        )
        for match in matches:
            embed.add_field(name=match['player_vs_string'],
                            value=match['round_string'], inline=True)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No {match_category}")
        # no match error

        # Reusable function that takes in the current matches and spits out upcoming/current matches for discord


async def check_for_end_of_tournament(ctx):
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

    # except Exception as err:
    #     await ctx.send(f"{config['ErrorMessages']['code_exception']} ```{err}```")


bot.run(config['Tokens']['discord_api_key'])
