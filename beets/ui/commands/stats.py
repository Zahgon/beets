"""The 'stats' command: show library statistics."""

import os

from beets import logging, ui
from beets.util import syspath
from beets.util.units import human_bytes, human_seconds

# Global logger.
log = logging.getLogger("beets")


def show_stats(lib, query, exact):
    """Shows some statistics about the matched items."""
    pass


def stats_func(lib, opts, args):
    pass


stats_cmd = ui.Subcommand(
    "stats", help="show statistics about the library or a query"
)
stats_cmd.parser.add_option(
    "-e", "--exact", action="store_true", help="exact size and time"
)
stats_cmd.func = stats_func
