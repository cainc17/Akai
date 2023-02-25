import datetime
import random
from typing import Optional
import aiohttp
import discord
from redbot.core import commands


class Quotes(commands.Cog):
    """Fetch quotes from an api."""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["qotd"])
    async def quoteoftheday(self, ctx: commands.Context) -> None:
        """Shows quote of the day."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://quotes.rest/qod?language=en",
                headers={"accept": "application/json"},
            ) as resp:
                if resp.status == 200:
                    json_response = await resp.json()
                    quote = json_response["contents"]["quotes"][0]["quote"]
                    embed = discord.Embed(title="Quote of the day!", color=0x2F3136)
                    embed.description = quote
                    embed.set_author(
                        name=ctx.author.name, icon_url=ctx.author.avatar_url
                    )
                    embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                    await ctx.send(embed=embed)

    @commands.command()
    async def quote(self, ctx: commands.Context):
        """Fetches a random quote."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as quote_json:
                q = await quote_json.json()  # Make sure to import json

        try:
            quote = q["content"]
            author = q["author"]
            embed = discord.Embed(
                title="Quote by {}".format(author.capitalize()),
                description=quote,
                color=random.randint(000000, 999999),
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.avatar_url,
            )
            embed.timestamp = datetime.datetime.now()
            await ctx.send(embed=embed)
        except:
            await ctx.send("An error occurred.")
