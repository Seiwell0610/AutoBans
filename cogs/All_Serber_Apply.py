import os
import sqlite3
import asyncio

import discord
import dropbox
from discord.ext import commands
from cogs.Reload import admin_list as al

print(f"{os.path.basename(__file__)}の読み込み完了")

cn = sqlite3.connect("Main_Data.db")
cu = cn.cursor()

dbxtoken = os.environ.get("dbxtoken")
dbx = dropbox.Dropbox(dbxtoken)
dbx.users_get_current_account()


def db_upload(filename):
    with open(f"{filename}", "rb") as fc:
        dbx.files_upload(fc.read(), f"/{filename}", mode=dropbox.files.WriteMode.overwrite)

def db_download(filename):
    with open(f"{filename}", "wb") as f:
        metadata, res = dbx.files_download(path=f"/{filename}")
        f.write(res.content)


class AllServerApply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def all_guild_apply(self, ctx, entry_user: commands.UserConverter):
        if not ctx.author.id in al:
            return await ctx.send("管理者専用コマンドです。")

        cu.execute(f"INSERT INTO all_guild_apply VALUES (?)", (entry_user.id,))
        cn.commit()
        user = ctx.guild.get_member(entry_user.id)
        for x in self.bot.guilds:
            role = discord.utils.get(x.roles, name="メンバー")
            await user.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}-> 全てのサーバーで{entry_user}から{role}を剥奪しました。")

def setup(bot):
    bot.add_cog(AllServerApply(bot))