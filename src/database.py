import redis
from redis.exceptions import ConnectionError

class cacheDB():
    """
        For now 0 is the league database with discord
    
    """
    def __init__(self, url) -> None:
        self.url = url
        self.client = None
        self.client_state = 0
        self.betting_time = 300
        pass

    def connect(self) -> None:
        try:
            if self.client_state == 2:
                self.client.close()
            self.client: redis.Redis[bytes] = redis.Redis.from_url(self.url, db=0)
            self.client_state = 1
        except ConnectionError:
            print("Cant connect to host")

    def connect_betting(self) -> None:
        try:
            if self.client_state == 1:
                self.client.close()
            self.client: redis.Redis[bytes] = redis.Redis.from_url(self.url, db=1)
            self.client_state = 2
        except ConnectionError:
            print("Cant connect to host")
    

    def store_user(self, discord_id, riot_user, puuid, author_discord_tag, strikes=0, points=500) -> None:
        if self.client is None or self.client_state == 2:
            self.connect()
        self.client.hset(discord_id, "riot_user", riot_user)
        self.client.hset(discord_id, "puuid", puuid)
        self.client.hset(discord_id, "discord_tag", author_discord_tag)
        self.client.hset(discord_id, "strikes", strikes)
        self.client.hset(discord_id, "points", 500)
    
    def get_user_field(self, discord_id, field) -> (bytes|None):
        # field can be riot_user or puuid, strikes, daily
        # e.g.  121210930139 -> meshh -> 12132323
        if self.client is None or self.client_state == 2:
            self.connect()
        return self.client.hget(discord_id, field)
    
    def set_user_field(self, discord_id, field, value) -> (bytes|None):
        # field can be riot_user or puuid
        # e.g.  121210930139 -> meshh -> 12132323
        if self.client is None or self.client_state == 2:
            self.connect()
        return self.client.hset(discord_id, field, value)
    
    def remove_user(self, discord_id):
        if self.client is None or self.client_state == 2:
            self.connect()
        if self.client.exists(discord_id):
            self.client.delete(discord_id)
            return True
    def remove_and_return_all(self, discord_id):
        if self.client is None or self.client_state == 2:
            self.connect()
        if self.client.exists(discord_id):
            all_info: dict = self.client.hgetall(discord_id)
            self.client.delete(discord_id)
            return all_info
    
    def get_all_users(self) -> list[str]:
        if self.client is None or self.client_state == 2:
            self.connect()
        return self.client.keys('*')
    
    def check_user_existence(self, discord_id):
        if self.client is None or self.client_state == 2:
            self.connect()
        return self.client.exists(str(discord_id))
    
    def increment_field(self, discord_id, field, amount=1):
        if self.client is None or self.client_state == 2:
            self.connect()
        return self.client.hincrby(discord_id, field, amount)
    
    def decrement_field(self, discord_id, field, amount=1):
        if self.client is None or self.client_state == 2:
            self.connect()
        neg_amount = -int(amount)
        print(neg_amount)
        return self.client.hincrby(discord_id, field, str(neg_amount))

    ############## Betting database ###########################

    # Enable betting for self.betting_time amount of time
    def enable_betting(self):
        print("Betting enabled")
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        self.client.set("enable", "true")
        self.client.expire("enable", time=self.betting_time)

    # Get the current betting state
    # Returns a boolean
    def get_betting_state(self):
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        state = self.client.get("enable")
        if state is None:
            return False
        return True if state.decode('utf8') == 'true' else False

    def store_bet(self, discord_id, author_discord_tag, decision, amount):
        points = self.get_user_field(discord_id, "points")
        if points is None:
            print("Not enough points")
            return False
        points = int(points.decode('utf8'))
        if points <= amount:
            print("Not enough points")
            return False
        self.decrement_field(discord_id, "points", amount)
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        bet = self.get_bet(discord_id, decision)
        key = discord_id + "_" + decision
        try:
            if bet == 0:
                print("Bet does not exist")
                self.client.hset(key, "amount", amount)
                self.client.hset(key, "discord_tag", author_discord_tag)
            else:
                print("Bet does exist")
                self.client.hincrby(key, "amount", amount)
                print(self.client.hget(key, "amount"))
        except ConnectionError as e:
            print(e)
            return False
        print("Successful")
        return True

    # Get current bet, 0 if fields/keys do not exist
    def get_bet(self, discord_id, decision):
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        key = discord_id + "_" + decision
        bet = self.client.hget(key, "amount")
        if bet is None:
            bet = 0
        else:
            bet = bet.decode('utf-8')
        return bet

    # Output {'believers': [{name: "", amount: 0, "discord_id": id}], 'doubters': [{name: "", amount: 0, "discord_id": id}]}
    def get_all_bets(self):
        print("Getting all bets")
        result = {'believers': [], 'doubters': []}
        users = self.get_all_users()
        users = [user.decode('utf8') for user in users]
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        for discord_id in users:
            for decision in ['believers', 'doubters']:
                key = discord_id + "_" + decision
                amount = self.client.hget(key, "amount")
                discord_tag = self.client.hget(key, "discord_tag")
                if amount is None or discord_tag is None:
                    continue
                result[decision].append({"name": discord_tag.decode('utf8'), "amount": amount.decode('utf8'), "discord_id": discord_id})
        print(result)
        return result

    def remove_all_bets(self):
        if self.client_state == 1 or self.client is None:
            self.connect_betting()
        for key in self.client.keys('*'):
            self.client.delete(key)
