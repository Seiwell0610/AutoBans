import os
import libneko

import discord
from discord.ext import commands

print(f"{os.path.basename(__file__)}の読み込み完了")

def default_buttons():
    from libneko.pag.reactionbuttons import (
        first_page,
        back_10_pages,
        previous_page,
        next_page,
        forward_10_pages,
        last_page
    )

    return (
        first_page(),
        back_10_pages(),
        previous_page(),
        next_page(),
        forward_10_pages(),
        last_page()
    )


buttons = default_buttons()


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        pages = [(discord.Embed(title="コマンド一覧", color=discord.Color.blue()))]

        pages[0].add_field(name="./entry <メンションまたはユーザーID>", value="ユーザーを登録します。", inline=False)
        pages[0].add_field(name="./release <メンションまたはユーザーID>", value="ユーザーの登録を解除します。", inline=False)
        pages[0].add_field(name="./apply", value="設定を反映します。(bot導入時に必ずに実行してください。)", inline=False)

        nav = libneko.pag.navigator.EmbedNavigator(ctx, pages, timeout=20, buttons=default_buttons())
        nav.start()
        await ctx.send(nav)


def setup(bot):
    bot.add_cog(Help(bot))
