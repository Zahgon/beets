from __future__ import annotations

import os
from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, NamedTuple, TypeVar

from confuse.exceptions import ConfigError

import beets
from beets import ui
from beets.dbcore.db import Migration
from beets.dbcore.pathutils import normalize_path_for_db
from beets.dbcore.types import MULTI_VALUE_DELIMITER
from beets.util import unique_list
from beets.util.lyrics import Lyrics

if TYPE_CHECKING:
    from collections.abc import Iterator

    from beets.dbcore.db import Model
    from beets.library import Library

T = TypeVar("T")


def chunks(lst: list[T], n: int) -> Iterator[list[T]]:
    """Yield successive n-sized chunks from lst."""
    pass


class MultiValueFieldMigration(Migration):
    """Backfill multi-valued field from legacy single-string values."""

    str_field: ClassVar[str]
    list_field: ClassVar[str]

    @cached_property
    def separators(self) -> list[str]:
        pass

    def convert_to_list_value(self, str_value: str) -> str:
        """Normalize legacy str value separators to the canonical delimiter."""
        pass

    def _migrate_data(
        self, model_cls: type[Model], current_fields: set[str]
    ) -> None:
        """Migrate legacy single-valued field to multi-valued field."""
        pass


class MultiGenreFieldMigration(MultiValueFieldMigration):
    """Backfill multi-valued genres from legacy single-string genre data."""

    str_field = "genre"
    list_field = "genres"

    @cached_property
    def separators(self) -> list[str]:
        """Return known separators that indicate multiple legacy genres."""
        pass


class MultiRemixerFieldMigration(MultiValueFieldMigration):
    """Backfill multi-valued remixers from legacy single-string remixer data."""

    str_field = "remixer"
    list_field = "remixers"


class MultiLyricistFieldMigration(MultiValueFieldMigration):
    """Backfill multi-valued lyricists from legacy single-string lyricist data."""

    str_field = "lyricist"
    list_field = "lyricists"


class MultiComposerFieldMigration(MultiValueFieldMigration):
    """Backfill multi-valued composers from legacy single-string composer data."""

    str_field = "composer"
    list_field = "composers"


class MultiArrangerFieldMigration(MultiValueFieldMigration):
    """Backfill multi-valued arrangers from legacy single-string arranger data."""

    str_field = "arranger"
    list_field = "arrangers"


class LyricsRow(NamedTuple):
    id: int
    lyrics: str


class LyricsMetadataInFlexFieldsMigration(Migration):
    """Move legacy inline lyrics metadata into dedicated flexible fields."""

    CHUNK_SIZE = 100

    def _migrate_data(self, model_cls: type[Model], _: set[str]) -> None:
        """Migrate legacy lyrics to move metadata to flex attributes."""
        pass


class RelativePathMigration(Migration):
    """Migrate path field to contain value relative to the music directory."""

    db: Library

    def _migrate_field(self, model_cls: type[Model], field: str) -> None:
        pass

    def _migrate_data(
        self, model_cls: type[Model], current_fields: set[str]
    ) -> None:
        pass
