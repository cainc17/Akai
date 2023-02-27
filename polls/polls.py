"""
MIT License

Copyright (c) 2023-present Akai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import discord
from redbot.core import commands


class Polls(commands.Cog):
    """Creates a poll with the given question and options"""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx: commands.Context, *, parameters: str):
        """Creates a poll with the given question and options, delimit using '|'."""

        _parameters = parameters.split("|")
        if len(_parameters) < 3:
            await ctx.send(
                f"Must enter a question with atleast 2 options.\nExample: `{ctx.clean_prefix}poll How are you? | Good. | Not so good.`"
            )
            return
        question = _parameters[0]
        options = _parameters[1:]

        if len(_parameters) > 10:
            await ctx.send("A poll cannot have more than 10 options.")
            return

        embed = discord.Embed(title=question, color=0xFFA500)

        for i, option in enumerate(options):
            embed.add_field(name=f"{i+1}. {option}", value="\u200b", inline=False)

        poll_message: discord.Message = await ctx.send(embed=embed)

        for i in range(len(options)):
            await poll_message.add_reaction(chr(127462 + i))
