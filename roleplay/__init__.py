from .roleplay import RolePlay

__red_end_user_data_statement__ = (
    "This cog does not persistently store data about users."
)


async def setup(bot):
    command = bot.get_command("hug")
    if command:
        bot.remove_command("hug")
    await bot.add_cog(RolePlay(bot))
