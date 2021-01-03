import os
import sqlite3
import asyncio

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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="メンバー")
        await member.add_roles(role)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def entry(self, ctx, entry_user: commands.UserConverter):
        on_entry_user = cu.execute(f"SELECT user_id FROM '{ctx.guild.id}' WHERE user_id = ?", (entry_user.id, )).fetchone()
        if on_entry_user is None:
            cu.execute(f"INSERT INTO '{ctx.guild.id}' VALUES (?)",(entry_user.id, ))
            cn.commit()
            db_upload(filename="Main_Data.db")
            role = discord.utils.get(ctx.guild.roles, name="メンバー")
            user = ctx.guild.get_member(entry_user.id)
            await user.remove_roles(role)
            em = discord.Embed(title="登録", colour=discord.Colour.green())
            em.add_field(name="登録されたユーザー", value=f"{entry_user}({entry_user.id})")
            await ctx.send(f"{ctx.author.mention}")
            await ctx.send(embed=em)

        else:
            await ctx.send(f"{ctx.author.mention}-> 既に登録されているユーザーです。")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def release(self, ctx, entry_user: commands.UserConverter):
        on_entry_user = cu.execute(f"SELECT user_id FROM '{ctx.guild.id}' WHERE user_id = ?", (entry_user.id,)).fetchone()
        if on_entry_user is None:
            return await ctx.send(f"{ctx.author.mention}-> 登録されていないユーザーのため削除できませんでした。")

        role = discord.utils.get(ctx.guild.roles, name="メンバー")
        user = ctx.guild.get_member(entry_user.id)
        await user.add_roles(role)
        cu.execute(f"DELETE FROM '{ctx.guild.id}' WHERE user_id = ?", (entry_user.id, ))
        cn.commit()
        db_upload(filename="Main_Data.db")
        em = discord.Embed(title="解除", colour=discord.Colour.purple())
        em.add_field(name="解除されたユーザー", value=f"{entry_user}({entry_user.id})")
        await ctx.send(f"{ctx.author.mention}")
        await ctx.send(embed=em)


    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def apply(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="メンバー")
        if role is None:
            permissions = discord.Permissions(send_messages=False, read_messages=True, read_message_history=True)
            await ctx.guild.create_role(name="メンバー", permissions=permissions)
            role = discord.utils.get(ctx.guild.roles, name="メンバー")

        ban_users = []
        for row in cu.execute(f"SELECT user_id FROM '{ctx.guild.id}'"):
            ban_users.append(row[0])

        msg = await ctx.send(f"0%完了")
        count = 0
        for member in ctx.guild.members:
            if not member.id in ban_users:
                if not role in member.roles:
                    await member.add_roles(role)
                    count += 1
                    await msg.edit(content=f"{round(count / len(ctx.guild.members) * 100)}%完了")
        await msg.edit(content="100%完了")
        await asyncio.sleep(1)
        await msg.delete()
        await ctx.send(f"{ctx.author.mention}-> 設定を反映しました。")


def setup(bot):
    bot.add_cog(AutoBan(bot))
