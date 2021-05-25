# This file is part of The Discord Archivist.
# Copyright (c) 2021 Arbaaz Laskar <arzkar.dev@gmail.com>
#
# The Discord Archivist is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Discord Archivist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with The Discord Archivist. If not, see <http://www.gnu.org/licenses/>.

from discord import Embed
from discord.ext.commands import command, Cog


class Help(Cog):
    def __init__(self, client):
        self.client = client

    @command()
    async def help(self, ctx):
        """ Command to show the info about the different bot commands
        """

        await ctx.trigger_typing()

        embed = Embed(
            title="Bot Usage Instructions",
            description="Only those user who have administrator permission can run these commands.\nThe bot needs `View Channel` & `Read Message History` to archive a channel. For convenience, you can give the bot administrator permission to archive private channels if you dont want to fiddle with channel permissions."
        )

        embed.add_field(
            name="To archive the channel.",
            value="`>archive`", inline=False
        )

        embed.add_field(
            name="To archive the channel and view the logfile to debug any issues.",
            value="`>archive log`", inline=False
        )

        await ctx.channel.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
