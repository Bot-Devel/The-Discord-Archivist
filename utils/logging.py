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

import logging
import os
from time import gmtime


def create_logger(server, channel_name):

    logging.Formatter.converter = gmtime
    logging.Formatter.default_time_format = '%Y-%m-%d %H:%M:%S %Z%z'
    log = logging.getLogger('The Discord Archivist Bot')

    # create directories for server
    try:
        log.info(
            f"Creating directories in : img/, epub/ & logs/")
        os.mkdir(f"data/img/{server.id}")
        os.mkdir(f"data/epub/{server.id}")
        os.mkdir(f"data/logs/{server.id}")
    except FileExistsError:
        pass

    # adding console handler
    # console_handler = logging.StreamHandler()
    # console_handler_format = '%(asctime)s | L%(lineno)d: %(message)s'
    # console_handler.setFormatter(logging.Formatter(console_handler_format))
    # log.addHandler(console_handler)

    # adding file handler for logfile
    file_handler_format = '%(asctime)s | %(levelname)s | L%(lineno)d: %(message)s'
    file_handler = logging.FileHandler(
        f'data/logs/{server.id}/{server.name}_{channel_name}.log')
    file_handler.setFormatter(logging.Formatter(file_handler_format))

    log.setLevel(logging.INFO)
    log.addHandler(file_handler)

    return log
