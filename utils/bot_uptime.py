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

from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('')


@app.route('/')
def home():
    return "Bot is online!"


def run():
    # production server using waitress
    serve(app, host="0.0.0.0", port=8082)


def start_server():
    t = Thread(target=run)
    t.start()
