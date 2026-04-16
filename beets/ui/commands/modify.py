"""The `modify` command: change metadata fields."""

from beets import library, ui
from beets.util import functemplate
from beets.util.deprecation import maybe_replace_legacy_field

from .utils import do_query


def modify_items(lib, mods, dels, query, write, move, album, confirm, inherit):
    """Modifies matching items according to user-specified assignments and
    deletions.

    `mods` is a dictionary of field and value pairse indicating
    assignments. `dels` is a list of fields to be deleted.
    """
    pass


def print_and_modify(obj, mods, dels):
    """Print the modifications to an item and return a bool indicating
    whether any changes were made.

    `mods` is a dictionary of fields and values to update on the object;
    `dels` is a sequence of fields to delete.
    """
    pass


def modify_parse_args(args, is_album: bool):
    """Split the arguments for the modify subcommand into query parts,
    assignments (field=value), and deletions (field!).  Returns the result as
    a three-tuple in that order.

    Replace legacy string fields with list equivalents, and supply deprecation
    warnings for the user.
    """
    mods = {}
    dels = []
    query = []
    for arg in args:
        if arg.endswith("!") and "=" not in arg and ":" not in arg:
            dels.append(arg[:-1])  # Strip trailing !.
        elif "=" in arg and ":" not in arg.split("=", 1)[0]:
            key, val = arg.split("=", 1)
            key = maybe_replace_legacy_field(key, is_album, modify=True)
            mods[key] = val
        else:
            query.append(arg)
    return query, mods, dels


def modify_func(lib, opts, args):
    pass


modify_cmd = ui.Subcommand(
    "modify", help="change metadata fields", aliases=("mod",)
)
modify_cmd.parser.add_option(
    "-m",
    "--move",
    action="store_true",
    dest="move",
    help="move files in the library directory",
)
modify_cmd.parser.add_option(
    "-M",
    "--nomove",
    action="store_false",
    dest="move",
    help="don't move files in library",
)
modify_cmd.parser.add_option(
    "-w",
    "--write",
    action="store_true",
    default=None,
    help="write new metadata to files' tags (default)",
)
modify_cmd.parser.add_option(
    "-W",
    "--nowrite",
    action="store_false",
    dest="write",
    help="don't write metadata (opposite of -w)",
)
modify_cmd.parser.add_album_option()
modify_cmd.parser.add_format_option(target="item")
modify_cmd.parser.add_option(
    "-y", "--yes", action="store_true", help="skip confirmation"
)
modify_cmd.parser.add_option(
    "-I",
    "--noinherit",
    action="store_false",
    dest="inherit",
    default=True,
    help="when modifying albums, don't also change item data",
)
modify_cmd.func = modify_func
