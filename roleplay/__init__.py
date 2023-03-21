from .roleplay import RolePlay

__red_end_user_data_statement__ = (
    "This cog does not persistently store data about users."
)


def setup(bot):
    command = bot.get_command("hug")
    if command:
        bot.remove_command(command)
    bot.add_cog(RolePlay(bot))
