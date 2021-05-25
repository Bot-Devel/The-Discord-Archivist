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

import os
from shutil import rmtree
import re
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

# to use repl+uptimerobot website monitor
from utils.bot_uptime import start_server

from utils.processing import build_epub
from utils.logging import create_logger

intents = discord.Intents.default()
intents.members = True


client = commands.Bot(command_prefix='>', help_command=None, intents=intents)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game(name=">help")
    )


@client.command(name="archive", aliases=['Archive'])
async def archive_channel(ctx):
    if ctx.message.author == client.user:
        return  # Do not reply to yourself

    if ctx.message.author.bot:
        return  # Do not reply to other bots

    if not ctx.author.guild_permissions.administrator:
        return await ctx.message.channel.send(
            embed=discord.Embed(
                description="You are missing Administrator permission to run this command."))

    message_history = await ctx.channel.history(
        limit=None, oldest_first=True).flatten()

    log = create_logger(ctx.message.guild, ctx.message.channel.name)
    log.info("Started Archiving")
    progress_msg = await ctx.channel.send(
        embed=discord.Embed(description="Started Archiving")
    )

    build_status = await build_epub(log, message_history, progress_msg)

    if build_status is True:
        log.info(f"Sending Epub to channel: {ctx.message.channel.name}")
        await progress_msg.edit(
            embed=discord.Embed(description=f"Sending Epub to channel: {ctx.message.channel.name}"))
        await ctx.channel.send(file=discord.File(
            f"data/epub/{ctx.message.guild.id}/{ctx.message.guild.name}_{ctx.message.channel.name}.epub"
        ))

        if re.search("log", ctx.message.content):
            await ctx.channel.send(file=discord.File(
                f"data/logs/{ctx.message.guild.id}/{ctx.message.guild.name}_{ctx.message.channel.name}.log"
            ))

        log.info(f"Removing epub/, img/ & logs/ directories for the server")
        rmtree(f"data/epub/{ctx.message.guild.id}")
        rmtree(f"data/img/{ctx.message.guild.id}")
        rmtree(f"data/logs/{ctx.message.guild.id}")
        await progress_msg.delete()


start_server()
client.load_extension("cogs.help")
client.run(TOKEN)
