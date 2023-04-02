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

import time
from typing import Optional
import discord
from redbot.core import commands, Config


class AwayFromKeyboard(commands.Cog):
    """Make the bot send a message whenever you are away from the keyboard."""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=4654651557)

        default_member = {
            "afk": False,
            "mentions": [],
            "afk_since": None,
            "message": None,
        }

        self.config.register_member(**default_member)

    async def add_afk_to_nickname(self, member: discord.Member) -> None:
        name = member.display_name
        new_name = "[AFK] " + name
        try:
            await member.edit(nick=new_name, reason="User went AFK.")
        except discord.HTTPException:
            pass

    async def remove_afk_from_nickname(self, member: discord.Member) -> None:
        if "[AFK]" in member.display_name:
            try:
                await member.edit(
                    nick=None,
                    reason="User removed AFK status.",
                )
            except discord.HTTPException:
                pass

    async def remove_afk(
        self, channel: discord.TextChannel, member: discord.Member
    ) -> None:
        mentions = (await self.config.member(member).mentions())[:10]
        await self.config.member(member).clear()
        await self.remove_afk_from_nickname(member)

        description = f"While you were AFK, you got **{len(mentions)}** ping(s):"

        for mention in mentions:
            description += f"\n・{mention['author']}・<t:{mention['timestamp']}:R>・[Jump]({mention['url']})"

        embed = discord.Embed(
            title=f"Welcome back, {member.name}",
            description=description,
            color=0x2B2D31,
        )
        try:

            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener("on_message_without_command")
    async def afk_listener(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot:
            return

        cog_disabled = await self.bot.cog_disabled_in_guild(self, message.guild)
        if cog_disabled:
            return

        member_data = await self.config.member(message.author).all()
        if member_data["afk"]:
            await self.remove_afk(message.channel, message.author)

        for member in message.mentions:
            member_data = await self.config.member(member).all()
            if member_data and member_data["afk"]:
                await message.channel.send(
                    f"{member.name} is AFK: {member_data['message'] or 'No Message'} (since <t:{member_data['afk_since']}:R>)",
                    delete_after=5,
                )
                config = self.config.member(member)

                async with config.mentions() as mentions:
                    new_mention = {
                        "author": message.author.name,
                        "timestamp": int(time.time()),
                        "url": message.jump_url,
                    }
                    mentions.append(new_mention)

    @commands.command(aliases=["away", "touchgrass"])
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    @commands.has_permissions(embed_links=True)
    async def afk(self, ctx: commands.Context, *, message: Optional[str] = None):
        """Make the bot send a message whenever you are away from the keyboard."""

        data = await self.config.member(ctx.author).all()
        if data and data["afk"]:
            await self.remove_afk(ctx.channel, ctx.author)
        else:
            user_data = {
                "afk": True,
                "mentions": [],
                "afk_since": int(time.time()),
                "message": message,
            }
            await self.config.member(ctx.author).set(user_data)

            embed = discord.Embed(
                description=f"✅ I set your AFK: {message or 'No Message'}",
                color=0x2B2D31,
            )

            await self.add_afk_to_nickname(ctx.author)

            await ctx.send(embed=embed)
