"""The 'completion' command: print shell script for command line completion."""

import os
import re

from beets import library, logging, plugins, ui
from beets.util import syspath

# Global logger.
log = logging.getLogger("beets")


def print_completion(*args):
    pass


completion_cmd = ui.Subcommand(
    "completion",
    help="print shell script that provides command line completion",
)
completion_cmd.func = print_completion
completion_cmd.hide = True


BASH_COMPLETION_PATHS = [
    b"/etc/bash_completion",
    b"/usr/share/bash-completion/bash_completion",
    b"/usr/local/share/bash-completion/bash_completion",
    # SmartOS
    b"/opt/local/share/bash-completion/bash_completion",
    # Homebrew (before bash-completion2)
    b"/usr/local/etc/bash_completion",
]


def completion_script(commands):
    """Yield the full completion shell script as strings.

    ``commands`` is alist of ``ui.Subcommand`` instances to generate
    completion data for.
    """
    pass
