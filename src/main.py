from discord_handler import discBot, add_cog
import asyncio
from config import Settings
async def main():
    settings = Settings()
    my_bot = discBot(token=settings.DISCORDTOKEN, hook=settings.WEBHOOK, channel_id=settings.CHANNELID)
    my_cogs = ["loop", "commands"]
    for cog in my_cogs:
        await add_cog(my_bot, cog)
    await my_bot.start_bot()

if __name__ == "__main__":
     asyncio.run(main())