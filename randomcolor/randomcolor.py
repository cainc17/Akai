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

from typing import Optional
import discord
from redbot.core import commands, Config
from discord.ext import tasks
import datetime
import re


class RandomColor(commands.Cog):
    """Automatically change role colour to a random hex daily."""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=54564545137)

        default_guild = {"role_id": None, "log_channel": None, "toggle": False}

        self.config.register_guild(**default_guild)

        self.sleep_time = None  # for debugging

        self.initialize()

    def initialize(self) -> None:

        if not self.color_change_task.is_running():
            self.color_change_task.start()

    def cog_unload(self) -> None:
        self.color_change_task.stop()

    async def log(
        self, guild: discord.Guild, message: str, color: discord.Colour
    ) -> None:
        channel_id = await self.config.guild(guild).log_channel()
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    embed = discord.Embed(description=message, color=color)
                    await channel.send(embed=embed)
                except discord.HTTPException:
                    pass

    async def change_role_colour(
        self, guild: discord.Guild, role: Optional[discord.Role] = None
    ) -> None:
        if not role:
            role = guild.get_role(await self.config(guild).role_id())

        color = discord.Colour.random()
        await role.edit(color=color, reason="Random Colour!")
        await self.log(
            guild,
            f"The colour for role {role.mention} has been changed to {color}",
            color,
        )

    @tasks.loop(hours=12)
    async def color_change_task(self) -> None:
        data = await self.config.all_guilds()
        for guild_id, guild_data in data:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            if not guild["toggle"]:
                return

            role = guild.get_role(guild_data["role_id"])
            if not role:
                await self.config.guild(guild).role_id.set(None)
                await self.config.guild(guild).toggle.set(None)
                await self.log(
                    guild, "The random colour role was not found!", discord.Colour.red()
                )

            await self.change_role_colour(guild, role)

    @color_change_task.before_loop
    async def wait_until_time(self):

        now = datetime.datetime.utcnow()

        task = self.color_change_task
        interval = datetime.timedelta(
            hours=task.hours, minutes=task.minutes, seconds=task.seconds
        )
        next_run = now.replace(hour=0, minute=0, second=0)

        while next_run > now:
            next_run -= interval
        while next_run < now:
            next_run += interval

        self.sleep_time = next_run

        await discord.utils.sleep_until(next_run)

    @commands.group(
        name="randomcolour", aliases=["randomcolor"], invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def randomcolour(self, ctx: commands.Context) -> None:
        """Change the hex of a role daily to a random colour."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @randomcolour.command(name="role")
    async def randomcolour_role(
        self, ctx: commands.Context, role: discord.Role
    ) -> None:
        """Set the random colour role."""
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.send(
                f"I cannot perform that action due to role hierarchy."
            )
        elif role.position >= ctx.author.top_role.position:
            if ctx.author.id == ctx.guild.owner.id:
                pass
            else:
                return await ctx.send(
                    f"I cannot perform that action due to role hierarchy."
                )

        embed = discord.Embed(
            description=f"Successfully changed the random colour role to {role.mention}",
            color=role.color,
        )

        await self.config.guild(ctx.guild).role_id.set(role.id)

        await ctx.send(embed=embed)

    @randomcolour.command(name="logchannel")
    async def randomcolour_logchannel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        """Set the random colour logchannel."""
        try:
            _embed = discord.Embed(
                title="I will send random colour role logs here!",
                color=discord.Colour.random(),
            )
            await channel.send(embed=_embed)
        except:
            await ctx.send(
                "I failed to send a message there, make sure to check if I have proper permissions."
            )
            return

        embed = discord.Embed(
            description=f"Successfully changed the random colour log channel to {channel.mention}",
            color=0x2B2D31,
        )

        await self.config.guild(ctx.guild).log_channel.set(channel.id)

        await ctx.send(embed=embed)

    @randomcolour.command(name="changecolour", aliases=["changecolor"])
    async def randomcolour_changecolour(self, ctx: commands.Context) -> None:
        """Force change the color of random color role."""
        await self.change_role_colour(ctx.guild)
        await ctx.tick()

    @randomcolour.command(name="toggle")
    async def randomcolour_toggle(self, ctx: commands.Context) -> None:
        """Toggle the random colour loop."""
        role = await self.config.guild(ctx.guild).role_id()
        if not role:
            await ctx.send(
                f"Set the random colour role first using `{ctx.clean_prefix}randomcolour role`."
            )
            return

        await self.config.guild(ctx.guild).toggle.set(True)
        await ctx.tick()
