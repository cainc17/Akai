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
            await poll_message.add_reaction(chr(127462 + i))

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

        poll = self.check_is_a_poll(message)
        if not poll:
            await ctx.send("That is not a poll message.")
            return

        # Get the list of options from the message embed
        embed = message.embeds[0]
        options = [field.name.split(". ")[1] for field in embed.fields]

        # Get the reactions from the message
        reactions = message.reactions

        # Generate a bar chart of the reaction counts
        counts = [0] * len(options)
        for reaction in reactions:
            try:
                index = options.index(reaction.emoji.name)
            except ValueError:
                continue
            counts[index] = (
                reaction.count - 1
            )  # subtract 1 to exclude the bot's reaction

        max_count = max(counts)
        if max_count == 0:
            bar_chart = "No votes yet"
        else:
            bar_chart = ""
            for i, option in enumerate(options):
                count = counts[i]
                bar_length = round(count / max_count * 10)
                bar_chart += (
                    f"{option}: {'█' * bar_length}{'-' * (10 - bar_length)} ({count})\n"
                )

        # Update the poll message embed description with the bar chart
        embed.description = bar_chart

        # Edit the poll message to indicate that it has ended
        embed.title += " (Ended)"
        embed.color = discord.Color.dark_grey()
        await message.edit(embed=embed)

        await ctx.send(f"Poll with ID {message_id} has ended.")
