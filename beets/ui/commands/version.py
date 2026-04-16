"""The 'version' command: show version information."""

from platform import python_version

import beets
from beets import plugins, ui


def show_version(*args):
    pass


version_cmd = ui.Subcommand("version", help="output version information")
version_cmd.func = show_version

__all__ = ["version_cmd"]
