# This file is part of beets.
# Copyright 2016, Fabrice Laporte
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Abstraction layer to resize images using PIL, ImageMagick, or a
public resizing proxy if neither is available.
"""

from __future__ import annotations

import os
import os.path
import platform
import re
import subprocess
from abc import ABC, abstractmethod
from contextlib import suppress
from enum import Enum
from itertools import chain
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import urlencode

from beets import logging, util
from beets.util import (
    LazySharedInstance,
    displayable_path,
    get_temp_filename,
    syspath,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

PROXY_URL = "https://images.weserv.nl/"

log = logging.getLogger("beets")


def resize_url(url: str, maxwidth: int, quality: int = 0) -> str:
    """Return a proxied image URL that resizes the original image to
    maxwidth (preserving aspect ratio).
    """
    pass


class LocalBackendNotAvailableError(Exception):
    pass


# Singleton pattern that the typechecker understands:
# https://peps.python.org/pep-0484/#support-for-singleton-types-in-unions
class NotAvailable(Enum):
    token = 0


_NOT_AVAILABLE = NotAvailable.token


class LocalBackend(ABC):
    NAME: ClassVar[str]

    @classmethod
    @abstractmethod
    def version(cls) -> Any:
        """Return the backend version if its dependencies are satisfied or
        raise `LocalBackendNotAvailableError`.
        """
        pass

    @classmethod
    def available(cls) -> bool:
        """Return `True` this backend's dependencies are satisfied and it can
        be used, `False` otherwise."""
        try:
            cls.version()
            return True
        except LocalBackendNotAvailableError:
            return False

    @abstractmethod
    def resize(
        self,
        maxwidth: int,
        path_in: bytes,
        path_out: bytes | None = None,
        quality: int = 0,
        max_filesize: int = 0,
    ) -> bytes:
        """Resize an image to the given width and return the output path.

        On error, logs a warning and returns `path_in`.
        """
        pass

    @abstractmethod
    def get_size(self, path_in: bytes) -> tuple[int, int] | None:
        """Return the (width, height) of the image or None if unavailable."""
        pass

    @abstractmethod
    def deinterlace(
        self,
        path_in: bytes,
        path_out: bytes | None = None,
    ) -> bytes:
        """Remove interlacing from an image and return the output path.

        On error, logs a warning and returns `path_in`.
        """
        pass

    @abstractmethod
    def get_format(self, path_in: bytes) -> str | None:
        """Return the image format (e.g., 'PNG') or None if undetectable."""
        pass

    @abstractmethod
    def convert_format(
        self,
        source: bytes,
        target: bytes,
        deinterlaced: bool,
    ) -> bytes:
        """Convert an image to a new format and return the new file path.

        On error, logs a warning and returns `source`.
        """
        pass

    @property
    def can_compare(self) -> bool:
        """Indicate whether image comparison is supported by this backend."""
        pass

    def compare(
        self,
        im1: bytes,
        im2: bytes,
        compare_threshold: float,
    ) -> bool | None:
        """Compare two images and return `True` if they are similar enough, or
        `None` if there is an error.

        This must only be called if `self.can_compare()` returns `True`.
        """
        # It is an error to call this when ArtResizer.can_compare is not True.
        raise NotImplementedError()

    @property
    def can_write_metadata(self) -> bool:
        """Indicate whether writing metadata to images is supported."""
        pass

    def write_metadata(self, file: bytes, metadata: Mapping[str, str]) -> None:
        """Write key-value metadata into the image file.

        This must only be called if `self.can_write_metadata()` returns `True`.
        """
        # It is an error to call this when ArtResizer.can_write_metadata is not True.
        raise NotImplementedError()


class IMBackend(LocalBackend):
    NAME = "ImageMagick"

    # These fields are used as a cache for `version()`. `_legacy` indicates
    # whether the modern `magick` binary is available or whether to fall back
    # to the old-style `convert`, `identify`, etc. commands.
    _version: tuple[int, int, int] | NotAvailable | None = None
    _legacy: bool | None = None

    @classmethod
    def version(cls) -> tuple[int, int, int]:
        """Obtain and cache ImageMagick version.

        Raises `LocalBackendNotAvailableError` if not available.
        """
        if cls._version is None:
            for cmd_name, legacy in (("magick", False), ("convert", True)):
                try:
                    out = util.command_output([cmd_name, "--version"]).stdout
                except (subprocess.CalledProcessError, OSError) as exc:
                    log.debug("ImageMagick version check failed: {}", exc)
                    cls._version = _NOT_AVAILABLE
                else:
                    if b"imagemagick" in out.lower():
                        pattern = rb".+ (\d+)\.(\d+)\.(\d+).*"
                        match = re.search(pattern, out)
                        if match:
                            cls._version = (
                                int(match.group(1)),
                                int(match.group(2)),
                                int(match.group(3)),
                            )
                            cls._legacy = legacy

        # cls._version is never None here, but mypy doesn't get that
        if cls._version is _NOT_AVAILABLE or cls._version is None:
            raise LocalBackendNotAvailableError()
        else:
            return cls._version

    convert_cmd: list[str]
    identify_cmd: list[str]
    compare_cmd: list[str]

    def __init__(self) -> None:
        """Initialize a wrapper around ImageMagick for local image operations.

        Stores the ImageMagick version and legacy flag. If ImageMagick is not
        available, raise an Exception.
        """
        self.version()

        # Use ImageMagick's magick binary when it's available.
        # If it's not, fall back to the older, separate convert
        # and identify commands.
        if self._legacy:
            self.convert_cmd = ["convert"]
            self.identify_cmd = ["identify"]
            self.compare_cmd = ["compare"]
        else:
            self.convert_cmd = ["magick"]
            self.identify_cmd = ["magick", "identify"]
            self.compare_cmd = ["magick", "compare"]

    def resize(
        self,
        maxwidth: int,
        path_in: bytes,
        path_out: bytes | None = None,
        quality: int = 0,
        max_filesize: int = 0,
    ) -> bytes:
        """Resize using ImageMagick.

        Use the ``magick`` program or ``convert`` on older versions. Return
        the output path of resized image.
        """
        pass

    def get_size(self, path_in: bytes) -> tuple[int, int] | None:
        pass

    def deinterlace(
        self,
        path_in: bytes,
        path_out: bytes | None = None,
    ) -> bytes:
        pass

    def get_format(self, path_in: bytes) -> str | None:
        pass

    def convert_format(
        self,
        source: bytes,
        target: bytes,
        deinterlaced: bool,
    ) -> bytes:
        pass

    @property
    def can_compare(self) -> bool:
        pass

    def compare(
        self,
        im1: bytes,
        im2: bytes,
        compare_threshold: float,
    ) -> bool | None:
        pass

    @property
    def can_write_metadata(self) -> bool:
        pass

    def write_metadata(self, file: bytes, metadata: Mapping[str, str]) -> None:
        pass


class PILBackend(LocalBackend):
    NAME = "PIL"

    @classmethod
    def version(cls) -> None:
        try:
            __import__("PIL", fromlist=["Image"])
        except ImportError:
            raise LocalBackendNotAvailableError()

    def __init__(self) -> None:
        """Initialize a wrapper around PIL for local image operations.

        If PIL is not available, raise an Exception.
        """
        self.version()

    def resize(
        self,
        maxwidth: int,
        path_in: bytes,
        path_out: bytes | None = None,
        quality: int = 0,
        max_filesize: int = 0,
    ) -> bytes:
        """Resize using Python Imaging Library (PIL).  Return the output path
        of resized image.
        """
        pass

    def get_size(self, path_in: bytes) -> tuple[int, int] | None:
        pass

    def deinterlace(
        self,
        path_in: bytes,
        path_out: bytes | None = None,
    ) -> bytes:
        pass

    def get_format(self, path_in: bytes) -> str | None:
        pass

    def convert_format(
        self,
        source: bytes,
        target: bytes,
        deinterlaced: bool,
    ) -> bytes:
        pass

    @property
    def can_compare(self) -> bool:
        pass

    def compare(
        self,
        im1: bytes,
        im2: bytes,
        compare_threshold: float,
    ) -> bool | None:
        # It is an error to call this when ArtResizer.can_compare is not True.
        raise NotImplementedError()

    @property
    def can_write_metadata(self) -> bool:
        pass

    def write_metadata(self, file: bytes, metadata: Mapping[str, str]) -> None:
        pass


BACKEND_CLASSES: list[type[LocalBackend]] = [
    IMBackend,
    PILBackend,
]


class ArtResizer:
    """A class that dispatches image operations to an available backend."""

    local_method: LocalBackend | None

    def __init__(self) -> None:
        """Create a resizer object with an inferred method."""
        # Check if a local backend is available, and store an instance of the
        # backend class. Otherwise, fallback to the web proxy.
        for backend_cls in BACKEND_CLASSES:
            try:
                self.local_method = backend_cls()
                log.debug("artresizer: method is {.local_method.NAME}", self)
                break
            except LocalBackendNotAvailableError:
                continue
        else:
            # FIXME: Turn WEBPROXY into a backend class as well to remove all
            # the special casing. Then simply delegate all methods to the
            # backends. (How does proxy_url fit in here, however?)
            # Use an ABC (or maybe a typing Protocol?) for backend
            # methods, such that both individual backends as well as
            # ArtResizer implement it.
            # It should probably be configurable which backends classes to
            # consider, similar to fetchart or lyrics backends (i.e. a list
            # of backends sorted by priority).
            log.debug("artresizer: method is WEBPROXY")
            self.local_method = None

    shared: LazySharedInstance[ArtResizer] = LazySharedInstance()

    @property
    def method(self) -> str:
        pass

    def resize(
        self,
        maxwidth: int,
        path_in: bytes,
        path_out: bytes | None = None,
        quality: int = 0,
        max_filesize: int = 0,
    ) -> bytes:
        """Manipulate an image file according to the method, returning a
        new path. For PIL or IMAGEMAGIC methods, resizes the image to a
        temporary file and encodes with the specified quality level.
        For WEBPROXY, returns `path_in` unmodified.
        """
        pass

    def deinterlace(
        self,
        path_in: bytes,
        path_out: bytes | None = None,
    ) -> bytes:
        """Deinterlace an image.

        Only available locally.
        """
        pass

    def proxy_url(self, maxwidth: int, url: str, quality: int = 0) -> str:
        """Modifies an image URL according the method, returning a new
        URL. For WEBPROXY, a URL on the proxy server is returned.
        Otherwise, the URL is returned unmodified.
        """
        pass

    @property
    def local(self) -> bool:
        """A boolean indicating whether the resizing method is performed
        locally (i.e., PIL or ImageMagick).
        """
        pass

    def get_size(self, path_in: bytes) -> tuple[int, int] | None:
        """Return the size of an image file as an int couple (width, height)
        in pixels.

        Only available locally.
        """
        pass

    def get_format(self, path_in: bytes) -> str | None:
        """Returns the format of the image as a string.

        Only available locally.
        """
        pass

    def reformat(
        self,
        path_in: bytes,
        new_format: str,
        deinterlaced: bool = True,
    ) -> bytes:
        """Converts image to desired format, updating its extension, but
        keeping the same filename.

        Only available locally.
        """
        pass

    @property
    def can_compare(self) -> bool:
        """A boolean indicating whether image comparison is available"""
        pass

    def compare(
        self,
        im1: bytes,
        im2: bytes,
        compare_threshold: float,
    ) -> bool | None:
        """Return a boolean indicating whether two images are similar.

        Only available locally.
        """
        pass

    @property
    def can_write_metadata(self) -> bool:
        """A boolean indicating whether writing image metadata is supported."""
        pass

    def write_metadata(self, file: bytes, metadata: Mapping[str, str]) -> None:
        """Write key-value metadata to the image file.

        Only available locally. Currently, expects the image to be a PNG file.
        """
        pass
