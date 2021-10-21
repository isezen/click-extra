# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
# All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

""" Logging utilities. """

import logging

import click_log
from click_log import simple_verbosity_option

# Initialize global logger.
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


def reset_logger():
    """Forces the logger level to reset at the end of each CLI execution, as it
    might pollute the logger state between multiple test calls.
    """
    logger.setLevel(logging.NOTSET)


def verbosity_option(*args, **kwargs):
    return simple_verbosity_option(
        logger,
        default="INFO",
        metavar="LEVEL",
        help="Either CRITICAL, ERROR, WARNING, INFO or DEBUG.",
    )