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
from redbot.core import commands, checks


number_emojis = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6,
    "7️⃣": 7,
    "8️⃣": 8,
    "9️⃣": 9,
    "🔟": 10,
}


class Polls(commands.Cog):
    """Creates a poll with the given question and options"""

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    def is_a_poll(self, message: discord.Message) -> bool:
        if message.author.id != self.bot.user.id or not message.embeds:
            return False

        if not message.embeds[0].footer:
            return False

        if not message.embeds[0].footer.text.startswith("Poll created by"):
            return False

        return True

    @commands.group(name="poll")
    @checks.has_permissions(manage_guild=True)
    async def poll(self, ctx: commands.Context):
        """Creates a poll with given questions and options."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @poll.command(name="create")
    async def poll_create(self, ctx: commands.Context, *, parameters: str):
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

        embed.set_footer(text=f"Poll created by {ctx.author}")

        poll_message: discord.Message = await ctx.send(embed=embed)

        for i in range(len(options)):
            number_emoji = (
                f"{i+1}\N{variation selector-16}\N{COMBINING ENCLOSING KEYCAP}"
            )
            await poll_message.add_reaction(number_emoji)

    @poll.command(name="end")
    async def poll_end(self, ctx: commands.Context, message_id: int):
        """Ends the poll with the given message ID."""
        try:
            message: discord.Message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send(f"Could not find a message with ID {message_id}")
            return
        except discord.Forbidden:
            await ctx.send("I do not have permission to fetch the message.")
            return
        except discord.HTTPException:
            await ctx.send("Failed to fetch the message.")
            return

        poll = self.is_a_poll(message)
        if not poll:
            await ctx.send("That is not a poll message.")
            return

        embed = message.embeds[0]
        options = [field.name for field in embed.fields]

        counts = [0] * len(options)
        for reaction in message.reactions:
            emoji_str = str(reaction.emoji)
            try:
                index = number_emojis[emoji_str]
            except KeyError:
                continue

            counts[index - 1] = reaction.count - 1

        max_count = max(counts)
        if max_count == 0:
            for i, option in enumerate(options):
                field_name = option
                embed.set_field_at(
                    i, name=field_name, value="No votes yet!", inline=False
                )
        else:
            for i, option in enumerate(options):
                count = counts[i]
                bar_length = round(count / max_count * 10)
                field_name = option
                field_value = f"{'█' * bar_length}{'-' * (10 - bar_length)} ({count})"
                embed.set_field_at(i, name=field_name, value=field_value, inline=False)

        # Edit the poll message to indicate that it has ended
        embed.title += " (Ended)"
        embed.color = discord.Color.dark_grey()
        embed.set_footer(text="")
        await message.edit(embed=embed)

        await ctx.send(f"Poll with ID {message_id} has ended.")
