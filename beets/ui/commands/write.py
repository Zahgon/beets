"""The `write` command: write tag information to files."""

import os

from beets import library, logging, ui
from beets.util import syspath

from .utils import do_query

# Global logger.
log = logging.getLogger("beets")


def write_items(lib, query, pretend, force):
    """Write tag information from the database to the respective files
    in the filesystem.
    """
    pass


def write_func(lib, opts, args):
    pass


write_cmd = ui.Subcommand("write", help="write tag information to files")
write_cmd.parser.add_option(
    "-p",
    "--pretend",
    action="store_true",
    help="show all changes but do nothing",
)
write_cmd.parser.add_option(
    "-f",
    "--force",
    action="store_true",
    help="write tags even if the existing tags match the database",
)
write_cmd.func = write_func
