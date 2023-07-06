import requests
import json
import datetime
class PlayerMissingError(Exception):
    pass

# Raise the custom error

class riotAPI():
    """
        Simple functions to get matches, puuid and matchid's
    """
    def __init__(self, api_key) -> None:
        self.api_key = api_key 
        self.params = {
            "api_key": self.api_key
        }
    def set_key(self, new_key):
        self.api_key = new_key

    def get_puuid(self, user):
        response = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}", params= self.params)
        print(response.status_code)
        response.raise_for_status()
        return json.loads(response.content)['puuid']
    def get_match_ids(self, method, credentials, count=10):
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
            params['count'] = 5
            response =requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids", params= self.params)
            print(response.status_code)
            response.raise_for_status()
            return json.loads(response.content)

    def get_match_details_by_matchID(self, match_id):
        #/lol/match/v5/matches/{matchId}
        response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}", params= self.params)
        response.raise_for_status()
        return json.loads(response.content)['info']['participants']
    
    def get_match_details_by_matchID_and_filter_for_puuid(self, match_id, puuid) -> list:
        #/lol/match/v5/matches/{matchId}
        # passed matchid and puuid
        # and receives the game data for player {puuid} in game {matchid}
        response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}", params= self.params)
        response.raise_for_status()
        content = json.loads(response.content)
        for player in content['info']['participants']:
            if player.get("puuid") == puuid:
                return player, content['info']['gameEndTimestamp'], content['info']['gameMode'], content['info']['queueId']
        return PlayerMissingError("No recent games found..")
    
    def get_match_details_by_user(self, user) -> list:
        puuid: dict = self.get_puuid(user)
        matchIDs: list = self.get_match_ids("puuid", puuid)

        matchinfo: list = []
        for matchID in matchIDs:
            match_details, game_end, game_mode, game_type= self.get_match_details_by_matchID_and_filter_for_puuid(matchID, puuid)
            diff = datetime.datetime.now().timestamp() - game_end/1000
            # time_difference = datetime.timedelta(seconds=diff)
            full_details = {
                "match_details": match_details,
                "game_mode": game_mode,
                "time_diff": diff,
                "game_type":game_type
            }
            matchinfo.append(full_details)
        return matchinfo
    
    def get_match_details_by_puuid(self, puuid) -> list:
        matchIDs: list = self.get_match_ids("puuid", puuid)

        matchinfo: list = []
        for matchID in matchIDs:
            match_details, game_end, game_mode, game_type= self.get_match_details_by_matchID_and_filter_for_puuid(matchID, puuid)
            diff = datetime.datetime.now().timestamp() - game_end/1000
            # time_difference = datetime.timedelta(seconds=diff)
            full_details = {
                "match_details": match_details,
                "game_mode": game_mode,
                "time_diff": diff,
                "game_type":game_type
            }
            matchinfo.append(full_details)
        return matchinfo

    def get_kda_by_puuid(self, puuid):
        print("getting kda")
        game_details_user = self.get_match_details_by_puuid(puuid)
        print("game details", game_details_user)
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
            print(game['game_type'])
            time_diff = datetime.timedelta(seconds=game['time_diff']).days
            game_mode = game_mode_mapping.get(game["game_type"], "Unranked")
            text += f'**{time_diff}** day(s) ago, {details["kills"]}/{details["deaths"]}/{details["assists"]} on {details["championName"]} in {game["game_mode"]}; {game_mode} \n'
        return text if flame == False else flame_text + text
            
    def get_kda_by_user(self, user):
        game_details_user = self.get_match_details_by_user(user)
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
            print(game['game_type'])
            time_diff = datetime.timedelta(seconds=game['time_diff']).days
            game_mode = game_mode_mapping.get(game["game_type"], "Unranked")
            text += f'**{time_diff}** day(s) ago, {details["kills"]}/{details["deaths"]}/{details["assists"]} on {details["championName"]} in {game["game_mode"]}; {game_mode} \n'
        return text if flame == False else flame_text + text
            
            

# for i in users

