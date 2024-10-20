# -*- coding: utf-8 -*-

#  This file is part of the Calibre-Web (https://github.com/janeczku/calibre-web)
#    Copyright (C) 2018-2019 OzzieIsaacs, cervinko, jkrehm, bodybybuddha, ok11,
#                            andy29485, idalin, Kyosfonica, wuqi, Kennyl, lemmsh,
#                            falgh1, grunjol, csitko, ytils, xybydy, trasba, vrabe,
#                            ruben-herold, marblepebble, JackED42, SiphonSquirrel,
#                            apetresc, nanu-c, mutschler
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import platform
import sqlite3
import importlib
from collections import OrderedDict

import flask
from flask_babel import gettext as _

from . import db, calibre_db, converter, uploader, constants, dep_check
from .render_template import render_title_template
from .usermanagement import user_login_required


about = flask.Blueprint('about', __name__)

modules = dict()
req = dep_check.load_dependencies(False)
opt = dep_check.load_dependencies(True)
for i in (req + opt):
    modules[i[1]] = i[0]
modules['Jinja2'] = importlib.metadata.version("jinja2")
try:
    modules['pySqlite'] = sqlite3.version
except Exception:
    pass
modules['SQLite'] = sqlite3.sqlite_version
sorted_modules = OrderedDict((sorted(modules.items(), key=lambda x: x[0].casefold())))

# Function to collect various system and version statistics.
def collect_stats():
    # If the NIGHTLY_VERSION constant hasn't been replaced, we're running a stable version.
    if constants.NIGHTLY_VERSION[0] == "$Format:%H$":
         # Replace 'b' with 'Beta' for the version string.
        calibre_web_version = constants.STABLE_VERSION['version'].replace("b", " Beta")
    else:
        # If running a nightly build, append nightly build information to the version string.
        calibre_web_version = (constants.STABLE_VERSION['version'].replace("b", " Beta") + ' - '
                               + constants.NIGHTLY_VERSION[0].replace('%', '%%') + ' - '
                               + constants.NIGHTLY_VERSION[1].replace('%', '%%'))
  # If the app is frozen (e.g., packaged as an executable), append "Exe-Version".
    if getattr(sys, 'frozen', False):
        calibre_web_version += " - Exe-Version"
  # If installed via PyPi, append "pyPi" to the version string.
    elif constants.HOME_CONFIG:
        calibre_web_version += " - pyPi"
# Creating a dictionary to store version information.
    _VERSIONS = {'Calibre Web': calibre_web_version}
    _VERSIONS.update(OrderedDict(
        Python=sys.version,
        Platform='{0[0]} {0[2]} {0[3]} {0[4]} {0[5]}'.format(platform.uname()),
    ))
   # Adding the version of ImageMagick (used for image manipulation, possibly for eBook covers).
    _VERSIONS.update(uploader.get_magick_version())
   # Adding the version of the Unrar utility (used to unpack RAR files)
    _VERSIONS['Unrar'] = converter.get_unrar_version()
   # Adding the version of the Calibre eBook converter (used for eBook format conversions).
    _VERSIONS['Ebook converter'] = converter.get_calibre_version()
   # Adding the version of Kepubify (used to convert eBooks to Kepub format).
    _VERSIONS['Kepubify'] = converter.get_kepubify_version()
   # Adding the sorted module information (collected earlier) to the versions dictionary.
    _VERSIONS.update(sorted_modules)
    return _VERSIONS


@about.route("/stats")
@user_login_required
def stats():
    counter = calibre_db.session.query(db.Books).count()
    authors = calibre_db.session.query(db.Authors).count()
    categories = calibre_db.session.query(db.Tags).count()
    series = calibre_db.session.query(db.Series).count()
    return render_title_template('stats.html', bookcounter=counter, authorcounter=authors, versions=collect_stats(),
                                 categorycounter=categories, seriecounter=series, title=_("Statistics"), page="stat")
