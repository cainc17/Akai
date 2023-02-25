from typing import Optional
import discord
from redbot.core import commands


class Device(commands.Cog):
    """Tells the device the user is using."""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def device(
        self, ctx: commands.Context, user: Optional[discord.Member] = None
    ) -> None:
        """Displays the device user is using."""
        user = user if user else ctx.author
        if user.bot:
            await ctx.send(
                embed=discord.Embed(
                    title="Ha! Bots don't have a physical device for you to check. But don't worry, all bots are safe and sound in the cloud, living their best virtual lives.",
                    color=0xFF0000,
                )
            )
            return
        devices = []
        if user.web_status != discord.Status.offline:
            devices.append("A Web 💻 device")
        if user.desktop_status != discord.Status.offline:
            devices.append("A Desktop 🖥️ device")
        if user.mobile_status != discord.Status.offline:
            devices.append("A Mobile 📱 device")
        if len(devices) == 0:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{user.name} is offline on all devices.", color=0xFF0000
                )
            )
            return
        deviceString = (
            devices[0]
            if len(devices) <= 1
            else ", ".join(devices[:-1]) + " and " + devices[-1]
        )
        embed = discord.Embed(
            title=f"{user.name} is using {deviceString}.", color=0x00FF00
        )
        await ctx.send(embed=embed)
