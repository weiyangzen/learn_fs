# sources/distributed-fs/tahoe-lafs/src/allmydata/util/encodingutil.py

## Purpose

This module normalizes Tahoe-LAFS command-line, filesystem, URL, and display encoding behavior across platforms after the Python 3 port. It favors UTF-8 for I/O, preserves Unicode filesystem APIs, and provides robust quoting for human-visible output.

## APIs and control flow

`canonical_encoding()`, `check_encoding()`, `_reload()`, `get_filesystem_encoding()`, and `get_io_encoding()` establish encodings. `argv_to_unicode()`, `argv_to_abspath()`, and deprecated `unicode_to_argv()` handle CLI values. `to_bytes()`, `from_utf8_or_none()`, and `unicode_to_url()` handle UTF-8 conversion. `quote_output()` and helpers quote bytes/unicode using single quotes where safe or backslash escapes for control/nonprintable bytes. Path helpers quote, extend, and convert Twisted `FilePath`s, list directories, and normalize Unicode to NFC.

## State, dependencies, risks, and tests

State is module globals `io_encoding` and `filesystem_encoding`. Dependencies include `six`, `sys`, `os`, `re`, `unicodedata`, Twisted `usage` and `FilePath`, local logging, assertions, and `fileutil.abspath_expanduser_unicode`.

Risks include locale mismatch, deprecated helpers still used by callers, quoting changing user-visible CLI output, Windows long-path handling interaction through `FilePath`, and `argv_to_abspath()` rejecting paths beginning with `-`. Test signals should cover invalid argv bytes, dash-prefixed paths, quote behavior for printable, newlines, invalid UTF-8 bytes, surrogate pairs, `FilePath` round-trips, NFC normalization, and platform-specific Windows path forms.
