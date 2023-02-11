import challonge


challonge.set_credentials("zak123", "rA21xWv5BFa3GURVotGMmtaIb5cyGu6Y2lcPxmm6")


# Tell pychallonge about your [CHALLONGE! API credentials](http://api.challonge.com/v1).

# Retrieve a tournament by its id (or its url).

async def GetTournament(id):
    tournament = challonge.tournaments.show(id)
    print(tournament)
    return tournament['name']


async def StartTournament(id):
    tournament = challonge.tournaments.start(id)
    return f"{tournament['name']} has begun."


# async def GetParticipants(id):
#     return challonge.participants.index(id)


async def GetOngoingMatches(id):
    participants = challonge.participants.index(id)
    matches = challonge.matches.index(id)
    # match ID's with names and add names to match list
    for participant in participants:
        id = participant['id']
        for match in matches:
            if id == match['player1_id']:
                match['player1_name'] = participant['name']
            elif id == match['player2_id']:
                match['player2_name'] = participant['name']
    open_matches = []

    # only return matches that need to be played
    for match in matches:
        if match['state'] == 'open':
            open_matches.append(match)

    return open_matches


# # Tournaments, matches, and participants are all represented as normal Python dicts.
# print(tournament["id"]) # 3272
# print(tournament["name"]) # My Awesome Tournament
# print(tournament["started_at"]) # None

# # Retrieve the participants for a given tournament.
# participants = challonge.participants.index(tournament["id"])
# print(len(participants)) # 13

# # Start the tournament and retrieve the updated information to see the effects
# # of the change.
# challonge.tournaments.start(tournament["id"])
# tournament = challonge.tournaments.show(tournament["id"])
# print(tournament["started_at"]) # 2011-07-31 16:16:02-04:00
