# Project
Just a small discord bot used for a group of friends. Mainly used to fetch players when they go in game and show the results after the end of a game.

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

## Disclaimer
Originally forked from another project, which has been deleted since 06-11-2023, latest commit on that repo: 1690abd83c26fa19fcb2e84dfdf04d78d67beff4.