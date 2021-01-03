import os
import sqlite3

import discord
import dropbox
from discord.ext import commands

print(f"{os.path.basename(__file__)}の読み込み完了")

cn = sqlite3.connect("Main_Data.db")
cu = cn.cursor()

dbxtoken = os.environ.get("dbxtoken")
dbx = dropbox.Dropbox(dbxtoken)
dbx.users_get_current_account()


def db_upload(filename):
    with open(f"{filename}", "rb") as fc:
        dbx.files_upload(fc.read(), f"/{filename}", mode=dropbox.files.WriteMode.overwrite)


class AutoBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        cu.execute(f"CREATE TABLE IF NOT EXISTS '{guild.id}' (user_id INTEGER)")  # 追加
        cn.commit()  # 反映
        db_upload(filename="Main_Data.db")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        cu.execute(f"DROP TABLE '{guild.id}'")  # 削除
        cn.commit()  # 反映
        db_upload(filename="Main_Data.db")

    @commands.command()
    async def entry(self, ctx, entry_user: commands.UserConverter):
        cu.execute(f"INSERT INTO '{ctx.guild.id}' VALUES (?)",(entry_user.id, ))
        cn.commit()
        db_upload(filename="Main_Data.db")
        await ctx.send(f"{ctx.author.mention}-> 登録しました")

    @commands.Cog.listener()
    async def on_message(self, message):
        ban_user = cu.execute(f"SELECT user_id FROM '{message.guild.id}' WHERE user_id = ?", (message.author.id,)).fetchone()

        if ban_user is None:
            return
        await message.delete()

        em = discord.Embed(title="ログ", description=f"{message.author}は発言禁止ユーザーとして登録されているため\n自動的にメッセージを削除しました。")
        em.add_field(name="削除されたメッセージ", value=f"{message.content}")
        await message.channel.send(embed=em, delete_after=5)


def setup(bot):
    bot.add_cog(AutoBan(bot))
