import challonge
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

challonge.set_credentials(
    config['Tokens']['challonge_username'], config['Tokens']['challonge_api_key'])


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


# async def ReportMatch(tournament_id, match_id, scores_csv):
#     print(tournament_id, match_id, scores_csv)
#     params = {'match[scores_csv]': f"{scores_csv}"}
#     return challonge.matches.update(tournament_id, match_id, params=params)


async def GetMatches(id):
    participants = challonge.participants.index(id)
    matches = challonge.matches.index(id)
    # match ID's with names and add names to match list
    if (len(matches) > 0):
        highest_round = 0
        for participant in participants:
            id = participant['id']
            for match in matches:
                if id == match['player1_id']:
                    match['player1_name'] = participant['name']
                    match['player1_seed'] = participant['seed']
                elif id == match['player2_id']:
                    match['player2_name'] = participant['name']
                    match['player2_seed'] = participant['seed']

                if highest_round < match['round']:
                    highest_round = match['round']

        # challonge uses negative numbers to describe how deep a losers match is, positive for winners
        for match in matches:
            if match['state'] == 'open':
                match['seed_total'] = match['player2_seed'] + match['player1_seed']

            if match['round'] == highest_round:
                match['round_string'] = 'Grand Finals'
            # elif match['round'] * -1 == highest_round:
            #     match['round_string'] = 'Loser Finals'
            elif match['round'] + 1 == highest_round:
                match['round_string'] = 'Winner Semifinals'
            # elif match['round'] * -1 + 1 == highest_round:
            #     match['round_string'] = 'Loser Semifinals'
            elif match['round'] > 0:
                match['round_string'] = f"Winners round {match['round']}"
            elif match['round'] < 0:
                match['round_string'] = f"Losers round {match['round'] * -1}"

        open_matches = []
        upcoming_matches = []
        stream_matches = []

        for match in matches:
            match['player_vs_string'] = f"{match.get('player1_name') if match.get('player1_name') else '???' } vs {match.get('player2_name') if match.get('player2_name') else '???'}"

            if match['state'] == 'open':
                open_matches.append(match)

            if match['state'] == 'pending':
                if match.get('player1_name') != None or match.get('player2_name') != None:
                    upcoming_matches.append(match)

        open_matches.sort(key=lambda x: x['seed_total'], reverse=False)

        if config['Options'].getboolean('assign_stream_matches_automatically'):
            stream_matches = [open_matches.pop(0)]

        result = {}
        result['open_matches'] = open_matches
        result['upcoming_matches'] = upcoming_matches
        result['stream_matches'] = stream_matches

        return result
    else:
        return None
