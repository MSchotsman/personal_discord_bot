import requests
import datetime
import aiohttp
import asyncio
class PlayerMissingError(Exception):
    pass
class PlayerMissingError(Exception):
    pass
# Raise the custom error

class riotAPI():
    """
        Simple functions to get matches, puuid and matchid's
    """
    #FIXME: UNCOUPLE THIS
    def __init__(self, api_key) -> None:
        self.api_key = api_key 
        self.params = {
            "api_key": self.api_key
        }
    def set_key(self, new_key):
        self.api_key = new_key

    async def get_puuid(self, user):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}", params= self.params) as response:
                response.raise_for_status()
                content: dict = await response.json()
                return content['puuid']
    
    async def get_match_ids(self, method, credentials, count=5):
        """
            Returns a list of matches by ID's in the form of:
            [
            "EUW1_6477028013",
            "EUW1_6476977329",
            ]
        """
        if method == "puuid":
            puuid = credentials
            params = self.params
            params['count'] = count
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids", params= self.params) as response:
                    response.raise_for_status()
                    content = await response.json()
                    return content

    async def get_match_details_by_matchID(self, match_id):
        #/lol/match/v5/matches/{matchId}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}", params= self.params) as response:
                response.raise_for_status()
                content = await response.json()
                return content['info']['participants']
    
    async def get_match_detail_by_matchID_and_filter_for_puuid(self, match_id, puuid):
        """
            Returns the details of a singular match for a singular player by passing the match ID and PUUID
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}", params= self.params) as response:
                response.raise_for_status()
                content = await response.json()
                matchinfo = dict()
                matchinfo['game_end'], matchinfo['game_mode'], matchinfo['game_type'] = content['info']['gameEndTimestamp'], \
                    content['info']['gameMode'], content['info']['queueId']
                for player in content['info']['participants']:
                    if player.get("puuid") == puuid:
                        matchinfo['match_details'] = player
                        return matchinfo

    
    async def get_multiple_match_details_by_matchIDs_and_filter_for_puuid(self, puuid, matchIDs) -> list:
        """
            Just a looped version of get_match_detail_by_matchID_and_filter_for_puuid.
            Returns the details of multiple matches for a singular player by passing the match ID and PUUID
        """
        matchesinfo: list = []
        for matchID in matchIDs:
            matchinfo: dict = await self.get_match_detail_by_matchID_and_filter_for_puuid(matchID, puuid)
            matchinfo['time_diff'] = datetime.datetime.now().timestamp() - matchinfo['game_end']/1000
            matchesinfo.append(matchinfo)
        return matchesinfo

    async def get_kda_by_puuid(self, puuid, count=10):
        matchIDs: list = await self.get_match_ids("puuid", puuid, count)
        game_details_user: list = await self.get_multiple_match_details_by_matchIDs_and_filter_for_puuid(puuid, matchIDs)
        flame = False
        flame_text = 'Nice job \n\n'
        text = ''
        game_mode_mapping = {
        420: "Ranked Solo/Duo",
        440: "Ranked Flex",
        400: "Normal"
        }
        for game in game_details_user:
            details = game["match_details"]
            time_diff = datetime.timedelta(seconds=game['time_diff']).days
            game_mode = game_mode_mapping.get(game["game_type"], "Unranked")
            result = "\u2705" if details["win"] else "\u274C"
            text += f'{result} **{time_diff}** day(s) ago | {details["kills"]}/{details["deaths"]}/{details["assists"]} on **{details["championName"]}** in __{game["game_mode"]}__ | {game_mode} \n'
        return text if flame == False else flame_text + text
    
    async def get_bad_kda_by_puuid(self, puuid, count=10, sleep_time=2):
        await asyncio.sleep(sleep_time)
        matchIDs: list = await self.get_match_ids("puuid", puuid, count=count)
        game_details_user: list = await self.get_multiple_match_details_by_matchIDs_and_filter_for_puuid(puuid, matchIDs)
        text = ''
        game_mode_mapping = {
        420: "Ranked Solo/Duo",
        440: "Ranked Flex",
        400: "Normal"
        }
        for game in game_details_user:
            details = game["match_details"]
            if details['deaths'] > (details['kills'] + details['assists']):
                time_diff = datetime.timedelta(seconds=game['time_diff']).days
                game_mode = game_mode_mapping.get(game["game_type"], "Unranked")
                result = "\u2705" if details["win"] else "\u274C"
                text += f'{result} **{time_diff}** day(s) ago  {details["kills"]}/{details["deaths"]}/{details["assists"]} on **{details["championName"]}** in __{game["game_mode"]}__ | {game_mode} \n'
        return text    
    
    async def get_kda_by_user(self, user, count =10):
        puuid = await self.get_puuid(user)
        matchIDs: list = await self.get_match_ids("puuid", puuid, count=count)
        game_details_user = await self.get_multiple_match_details_by_matchIDs_and_filter_for_puuid(puuid, matchIDs)
        flame = False
        flame_text = 'Nice job  \n\n'
        text = ''
        game_mode_mapping = {
        420: "Ranked Solo/Duo",
        440: "Ranked Flex",
        400: "Normal"
        }
        for game in game_details_user:
            details = game["match_details"]
            time_diff = datetime.timedelta(seconds=game['time_diff']).days
            game_mode = game_mode_mapping.get(game["game_type"], "Unranked")
            result = "\u2705" if details["win"] else "\u274C"
            text += f'{result} **{time_diff}** day(s) ago | {details["kills"]}/{details["deaths"]}/{details["assists"]} on **{details["championName"]}** in __{game["game_mode"]}__ | {game_mode} \n'
        return text if flame == False else flame_text + text
            
    async def get_highest_damage_taken_by_puuid(self, puuid, count, sleep_time, discord_id):
        await asyncio.sleep(sleep_time)
        matchIDs: list = await self.get_match_ids(method="puuid", credentials=puuid, count=count)
        game_details_user = await self.get_multiple_match_details_by_matchIDs_and_filter_for_puuid(puuid, matchIDs)
        player_details = {}
        player_details['taken'], player_details['champion'], player_details['disc_id'] = 0, '', discord_id
        for game in game_details_user:
            if game["match_details"]['totalDamageTaken'] > player_details['taken'] and game["game_mode"] not in ["ARAM", "URF", "CHERRY"]:
                player_details['taken'] = game["match_details"]['totalDamageTaken']
                player_details['champion'] = game["match_details"]["championName"]
        
        return player_details
    

# from config import *
# async def main():
#     settings = Settings()
#     riot_api = riotAPI(settings.RIOTTOKEN)
#     puuids = ['ftCv851wC2M95ROX3CQPVtxLdc2V8Od4EBfsjfvSgguvuOqvuBRcdWpuPjLYEy0bT5WKkyl43qFl1w', \
#               'SEV_5s1jFp9mfXed2gjosvfaRLq15JP86IWIolwUKnc5WwHvrIUveapZWf7BjO-dSqvJ_brA9FQlRA', \
#                 'NbE-Y8A7afr6fhaZK6XwqoFkQkKPDOBh_M4X6QgR5qXQqjwt3UgbIWRWTlBjaoooXmQOMOd9-91F1Q', \
#                     'A2sy0Y_gCeayApKm0pFAB54uwbwlEKuPZ13awDMEMJgKKME7zpu4SSQw59Yxhi0AnTSzhIrJbMwkYQ']
#     tasks = []
#     sleep_time = 0.5
#     for puuid in puuids:
#     # puuid = await riot_api.get_puuid("meshh")
#     # matches= await riot_api.get_match_ids("puuid", puuid)
#     # matches_details_user = await riot_api.get_multiple_match_details_by_matchIDs_and_filter_for_puuid(puuid, matchIDs=matches)
#     # print(matches_details_user)
#         print(sleep_time)
#         tasks.append(riot_api.get_highest_damage_taken_by_puuid(puuid, count=10, sleep_time=sleep_time, discord_id= 123124134))
#         sleep_time += 2
#     try:
#         result = await asyncio.gather(*tasks)
#         print(result)
#     except aiohttp.ClientResponseError as e:
#         print(e.message, e.status)
#         print("beep")
#     top_5 = sorted(result, key=lambda x: x['taken'], reverse=True)[:2]
#     print(top_5)
# asyncio.run(main())

