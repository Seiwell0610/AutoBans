import discord
import asyncio
import traceback
from discord.ext import commands
import os
import dropbox
from datetime import datetime

token = os.environ.get("TOKEN")
prefix = "./"
loop = asyncio.new_event_loop()

dbxtoken = os.environ.get("dbxtoken")
dbx = dropbox.Dropbox(dbxtoken)
dbx.users_get_current_account()


async def run():
    bot = MyBot()
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), loop=loop, intents=discord.Intents.all())
        self.remove_command('help')

    async def on_ready(self):
        path = "./cogs"
        for cog in os.listdir(path):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    self.reload_extension(f"cogs.{cog[:-3]}")

        await self.change_presence(activity=discord.Game(name=f"{prefix}help | {len(self.guilds)}guilds"))
        """em_time = datetime.now().strftime("%Y年%m月%d日-%H:%M")
        em = discord.Embed(title="オンラインになりました。", color=discord.Color.green())
        em.set_footer(text=f"{em_time}")
        await self.get_channel(778023527256424500).send(embed=em)"""

    async def on_guild_join(self, _):
        await self.change_presence(activity=discord.Game(name=f"{prefix}help | {len(self.guilds)}guilds"))

    async def on_guild_remove(self, _):
        await self.change_presence(activity=discord.Game(name=f"{prefix}help | {len(self.guilds)}guilds"))

    async def on_command_error(self, ctx, error1):
        if isinstance(error1, (commands.CommandNotFound, commands.CommandInvokeError)):
            return


if __name__ == '__main__':
    try:
        print("Logged in as")
        with open("Main_Data.db", "wb") as f:
            metadata, res = dbx.files_download(path=f"/Main_Data.db")
            f.write(res.content)
        print(f"Main_Data.dbのダウンロード完了")

        main_task = loop.create_task(run())
        loop.run_until_complete(main_task)
        loop.close()

    except Exception as error:
        print("エラー情報\n" + traceback.format_exc())
