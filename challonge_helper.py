import challonge
import datetime
from pytz import timezone

challonge.set_credentials("zak123", "rA21xWv5BFa3GURVotGMmtaIb5cyGu6Y2lcPxmm6")


# Tell pychallonge about your [CHALLONGE! API credentials](http://api.challonge.com/v1).

# Retrieve a tournament by its id (or its url).

async def GetTournament(id):
    return challonge.tournaments.show(id)


async def StartTournament(id):
    tournament = challonge.tournaments.start(id)
    return f"{tournament['name']} has begun."

async def EndTournament(id):
    return challonge.tournaments.finalize(id)

async def GetParticipants(id):
    return challonge.participants.index(id)


async def GetMatches(id):
    participants = challonge.participants.index(id)
    matches = challonge.matches.index(id)
    # match ID's with names and add names to match list
    highest_round = 0
    for participant in participants:
        id = participant['id']
        for match in matches:
            if id == match['player1_id']:
                match['player1_name'] = participant['name']
            elif id == match['player2_id']:
                match['player2_name'] = participant['name']

            if highest_round < match['round']:
                highest_round = match['round']

        for match in matches:
            if match['round'] == highest_round:
                match['round_string'] = 'Grand Finals'
            elif match['round'] * -1 == highest_round:
                match['round_string'] = 'Loser Finals'
            elif match['round'] + 1 == highest_round:
                match['round_string'] = 'Winner Semifinals'
            elif match['round'] * -1 + 1 == highest_round:
                match['round_string'] = 'Loser Semifinals'
            elif match['round'] > 0:
                match['round_string'] = f"Winners round {match['round']}"
            elif match['round'] < 0:
                match['round_string'] = f"Losers round {match['round'] * -1}"

    return matches


