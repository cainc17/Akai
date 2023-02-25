from .device import Device


def setup(bot):
    bot.add_cog(Device(bot))
