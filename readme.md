# Disclaimer
Originally forked from another project, which has been deleted since 06-11-2023, latest commit: 0591a4c25a2174176bce5a82a7d76fd897eb3398.
## Docker
Containers can be ran by installing docker and docker compose.
Default path is set to /app/ this path contains the .env file with the follow:
- DISCORDTOKEN: str
- CHANNELID: int
- JAILROLE: int
- RIOTTOKEN:str
- REDISURL: str
- PLAYERROLE: int
- GROLE: int
- PINGROLE: int
- SUPERUSER: int

Having this .env file somewhere else means you are forced to change this path in the ```docker-compose.yml```.
Running ```docker-compose up --build``` or ```docker compose up --build``` will start the containers.
