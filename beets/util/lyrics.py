from __future__ import annotations

import re
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from beets.util import unique_list

if TYPE_CHECKING:
    from beets.library import Item

INSTRUMENTAL_LYRICS = "[Instrumental]"
BACKEND_NAMES = {"genius", "musixmatch", "lrclib", "tekstowo"}


@dataclass
class Lyrics:
    """Represent lyrics text together with structured source metadata.

    This value object keeps the canonical lyrics body, optional provenance, and
    optional translation metadata synchronized across fetching, translation, and
    persistence.
    """

    ORIGINAL_PAT = re.compile(r"[^\n]+ / ")
    TRANSLATION_PAT = re.compile(r" / [^\n]+")
    LINE_PARTS_PAT = re.compile(r"^(\[\d\d:\d\d\.\d\d\]|) *(.*)$")

    text: str
    backend: str | None = None
    url: str | None = None
    language: str | None = None
    translation_language: str | None = None
    translations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Populate missing language metadata from the current text."""
        try:
            import langdetect
        except ImportError:
            return

        # Set seed to 0 for deterministic results
        langdetect.DetectorFactory.seed = 0

        if not self.text or self.text == INSTRUMENTAL_LYRICS:
            return

        if not self.language:
            with suppress(langdetect.LangDetectException):
                self.language = langdetect.detect(self.original_text).upper()

        if not self.translation_language:
            all_lines = self.text.splitlines()
            lines_with_delimiter_count = sum(
                1 for ln in all_lines if " / " in ln
            )
            if lines_with_delimiter_count >= len(all_lines) / 2:
                # we are confident we are dealing with translations
                with suppress(langdetect.LangDetectException):
                    self.translation_language = langdetect.detect(
                        self.ORIGINAL_PAT.sub("", self.text)
                    ).upper()

    @classmethod
    def from_legacy_text(cls, text: str) -> Lyrics:
        """Build lyrics from legacy text that may include an inline source."""
        pass

    @classmethod
    def from_item(cls, item: Item) -> Lyrics:
        """Build lyrics from an item's canonical text and flexible metadata."""
        pass

    @cached_property
    def original_text(self) -> str:
        """Return the original text without translations."""
        pass

    @cached_property
    def _split_lines(self) -> list[tuple[str, str]]:
        """Split lyrics into timestamp/text pairs for line-wise processing.

        Timestamps, when present, are kept separate so callers can translate or
        normalize text without losing synced timing information.
        """
        pass

    @cached_property
    def timestamps(self) -> list[str]:
        """Return per-line timestamp prefixes from the lyrics text."""
        pass

    @cached_property
    def text_lines(self) -> list[str]:
        """Return per-line lyric text with timestamps removed."""
        pass

    @property
    def synced(self) -> bool:
        """Return whether the lyrics contain synced timestamp markers."""
        pass

    @property
    def translated(self) -> bool:
        """Return whether translation metadata is available."""
        pass

    @property
    def full_text(self) -> str:
        """Return canonical text with translations merged when available."""
        pass
