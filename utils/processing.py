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

from ebooklib import epub
from PIL import Image
import io
import os
import random
import string
from discord import Embed
from datetime import timezone, datetime


image_types = ["png", "jpeg", "jpg"]
curr_time = datetime.utcnow().replace(
    tzinfo=timezone.utc).strftime(r'%-d %b, %Y at %H:%M:%S %Z%z')


async def build_epub(log, message_history, progress_msg):

    # get metadata
    for message in message_history:
        channel_name = str(message.channel)
        channel_id = str(message.channel.id)
        server_name = str(message.channel.guild)
        server_id = str(message.channel.guild.id)

    log.info("Building Epub")
    await progress_msg.edit(
        embed=Embed(description="Building Epub"))

    book = epub.EpubBook()

    # set metadata
    book.set_title(channel_name)
    book.set_language('en')
    book.add_author('The Discord Archivist Bot')

    chapters = []
    author_info = {}
    msg_pin_counter = 0

    log.info("Processing Message history")
    await progress_msg.edit(
        embed=Embed(description="Building Epub"))

    for message in message_history:
        empty_flag = 0

        if message.content or message.attachments:

            if str(message.author.name) not in author_info:
                author_info[str(message.author.name)] = 1
            else:
                author_info[str(message.author.name)
                            ] = author_info[str(message.author.name)] + 1

            msg_pin = ""
            if message.pinned:
                log.info(
                    f"Pinned message found, saving at Message: {str(message.author.name)} {author_info[str(message.author.name)]} {msg_pin}")
                await progress_msg.edit(
                    embed=Embed(
                        description=f"Pinned message found at Message: {str(message.author.name)} {author_info[str(message.author.name)]} {msg_pin}"))

                msg_pin_counter += 1
                msg_pin = "(Pinned)"

            time = message.created_at.replace(tzinfo=timezone.utc).strftime(
                r'%-d %b, %Y at %H:%M:%S %Z%z')

            c1 = epub.EpubHtml(title=f"{str(message.author.name)} {author_info[str(message.author.name)]} {msg_pin}",
                               file_name=f'{str(message.author.name)}_{str(author_info[str(message.author.name)])}.xhtml', lang='en')

            c1.content = f"<h2>{str(message.author.name)} {author_info[str(message.author.name)]} {msg_pin}</h2>\n<hr><p>Author Username: {message.author}<br />Author ID:  {message.author.id}<br />Datetime: {time}<br />\n<hr><br />"

            if message.reference:
                message_ref = message.reference  # message id of reply
                message_reply = await message.channel.fetch_message(message_ref.message_id)

                if message_reply.content or message_reply.attachments:
                    c1.content += '<i><u>Message Reply to:</u></i><br />'
                    c1, book, empty_flag = await get_message_data(
                        empty_flag,
                        log, message_reply, progress_msg, server_id, author_info, c1, book)
                    c1.content += '\n<hr align="left" style="width: 50%" />'

            c1, book, empty_flag = await get_message_data(
                empty_flag,
                log, message, progress_msg, server_id, author_info, c1, book)

        if empty_flag == 0:
            chapters.append(c1)

    message_authors = []
    for author in author_info.keys():
        message_authors.append(author)
    message_authors = ", ".join(message_authors)

    # pop out the last message which is the bot command i.e. >archive
    chapters.pop(-1)

    # About chapter
    about = epub.EpubHtml(title='About',
                          file_name='about.xhtml', lang='en')
    about.content = f'''
    <html><head></head>
        <body>
            <h1>{server_name}: {channel_name}</h1>
            <hr>
            <p> Channel: <br />
                    <font style="margin-left: 50px">Name: {channel_name}</font><br />
                    <font style="margin-left: 50px">ID: {channel_id}</font><br /><br />

                Server: <br />
                    <font style="margin-left: 50px">Name: {server_name}</font><br />
                    <font style="margin-left: 50px">ID: {server_id}</font><br /><br />

                Messages: <br />
                    <font style="margin-left: 50px">Total Messages: {len(chapters)}</font><br />
                    <font style="margin-left: 50px">Pinned Messages: {msg_pin_counter}</font><br />
                    <font style="margin-left: 50px">Total Message Authors: {len(author_info)}</font><br />
                    <font style="margin-left: 50px">Message Authors: {message_authors}</font><br /><br />

                Created by <a href="https://github.com/arzkar/The-Discord-Archivist">The Discord Archivist Bot </a> on {curr_time} <br />
            </p>
        </body>
    </html>
    '''

    book.add_item(about)

    # TODO: Duplicate chapter name bug due to The Archivist Embed?
    for chapter in chapters:
        book.add_item(chapter)

    book.toc = [
        epub.Link('about.xhtml', 'About', 'about')]+chapters

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # document style
    doc_style = epub.EpubItem(
        uid="doc_style",
        file_name="style/main.css",
        media_type="text/css",
        content=open("epub_style.css").read()
    )
    book.add_item(doc_style)

    nav_page = epub.EpubNav(uid='book_toc', file_name='toc.xhtml')
    nav_page.add_item(doc_style)
    book.add_item(nav_page)

    # adding book spine
    book.spine = [about, nav_page] + chapters

    log.info(
        f"Writing epub: data/epub/{server_id}/{server_name}_{channel_name}.epub")

    await progress_msg.edit(
        embed=Embed(
            description=f"Writing epub: data/epub/{server_id}/{server_name}_{channel_name}.epub"))

    epub.write_epub(
        f'data/epub/{server_id}/{server_name}_{channel_name}.epub', book, {})

    log.info("Epub Created")
    await progress_msg.edit(
        embed=Embed(description="Epub Created"))

    return True


async def get_message_data(empty_flag, log, message, progress_msg, server_id, author_info, c1, book):
    img_flag = 0

    # adding line breaks
    message_content = message.content.splitlines()
    message_content = "<br />".join(message_content)

    c1.content += message_content

    img_id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(image) for image in image_types):
                img_flag = 1

                log.info(
                    f"Image found, saving data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png")
                await progress_msg.edit(
                    embed=Embed(
                        description=f"Image found, saving data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png"))

                await attachment.save(f"data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png")

                c1.content += f'<br /><img alt={str(message.author.name)}_{str(author_info[str(message.author.name)])} src="data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png"></p>'

            elif not message.content:
                empty_flag = 1
                continue
    else:
        c1.content += u'</p>'

    if img_flag == 1:

        # load Image file
        img1 = Image.open(
            f'data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png')

        img1 = img1.convert('RGB')
        b = io.BytesIO()
        img1.save(b, 'jpeg')
        b_image1 = b.getvalue()

        # define Image file path in .epub
        image1_item = epub.EpubItem(
            uid=f'{str(message.author.name)}_{str(author_info[str(message.author.name)])}',
            file_name=f'data/img/{server_id}/{str(message.author.name)}_{str(author_info[str(message.author.name)])}_{img_id}.png',
            media_type='image/jpeg', content=b_image1)

        book.add_item(image1_item)

    return c1, book, empty_flag
