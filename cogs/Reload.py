import os

from discord.ext import commands



class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        msg = await ctx.send("更新中")
        for cog in os.listdir("./cogs"):
            if cog == 'Reload.py':
                continue
            if cog.endswith(".py"):
                try:
                    self.bot.reload_extension(f"cogs.{cog[:-3]}")
                except commands.ExtensionNotLoaded:
                    self.bot.load_extension(f"cogs.{cog[:-3]}")
        await msg.delete()
        await ctx.send(f"{ctx.author.mention}-> 更新が完了しました。")


def setup(bot):
    bot.add_cog(System(bot))
