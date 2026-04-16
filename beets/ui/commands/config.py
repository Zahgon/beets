"""The 'config' command: show and edit user configuration."""

import os

from beets import config, ui
from beets.util import displayable_path, editor_command, interactive_open


def config_func(lib, opts, args):
    # Make sure lazy configuration is loaded
    pass


def config_edit(cli_options):
    """Open a program to edit the user configuration.
    An empty config file is created if no existing config file exists.
    """
    path = cli_options.config or config.user_config_path()
    editor = editor_command()

    if not editor:
        raise ui.UserError(
            "Please set the VISUAL or EDITOR environment variable to edit"
            " configuration."
        )
    try:
        if not os.path.isfile(path):
            open(path, "w+").close()
        interactive_open([path], editor)
    except FileNotFoundError:
        raise ui.UserError(f"Editor {editor!r} not found.")
    except OSError as exc:
        raise ui.UserError(f"Could not edit configuration: {exc}")


config_cmd = ui.Subcommand("config", help="show or edit the user configuration")
config_cmd.parser.add_option(
    "-p",
    "--paths",
    action="store_true",
    help="show files that configuration was loaded from",
)
config_cmd.parser.add_option(
    "-e",
    "--edit",
    action="store_true",
    help="edit user configuration with $VISUAL (or $EDITOR)",
)
config_cmd.parser.add_option(
    "-d",
    "--defaults",
    action="store_true",
    help="include the default configuration",
)
config_cmd.parser.add_option(
    "-c",
    "--clear",
    action="store_false",
    dest="redact",
    default=True,
    help="do not redact sensitive fields",
)
config_cmd.func = config_func
