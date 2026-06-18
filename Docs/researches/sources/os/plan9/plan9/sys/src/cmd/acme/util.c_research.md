# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/util.c

This file provides Acme utility functions for UTF conversion, warnings, error windows, allocation, rune helpers, mouse restore, and new-window placement.

Key behavior:
- `cvttorunes()` converts byte input to runes while eliding NULs and reporting consumed bytes/runes.
- `error()` reports fatal error, removes the Acme error service file, and aborts.
- `errorwin()`/`errorwinforwin()` create or find `+Errors` windows, preserving directory/include context.
- `warning()` queues warning text by `Mntdir`; `flushwarnings()` writes queued warnings into error windows in buffered chunks.
- `runetobyte()` and `bytetorune()` convert between rune arrays and UTF strings.
- `isalnum()`, `skipbl()`, `findbl()`, `rgetc()`, and `tgetc()` support parsers/searchers.
- `emalloc()`, `erealloc()`, and `estrdup()` are checked allocation helpers.
- `makenewwindow()` chooses the active/best column and split point for new windows.

Important details:
- Warning buffers are per mount directory, and `Mntdir` refs are held until warnings flush.
- `flushwarnings()` is called with the row locked and writes through `textbsinsert()` to process backspaces.
- `isalnum()` treats most non-control non-punctuation runes as alphanumeric.
- New-window placement prefers active column, selection column, caller column, then last column.

Filesystem relevance:
- Supports error reporting for filesystem-mounted commands and path-aware `+Errors` windows.
