# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_ntfs.c

Read status: complete.

Purpose: Win32/Windows NT filesystem support for Ghostscript.

Main logic:
- Provides binary/text mode switching via `_setmode`/`setmode`.
- Defines Windows/DOS file constants: list separator `;`, binary suffix `b`, modes `rb`/`wb`.
- Implements file enumeration with `FindFirstFile` and `FindNextFile`.
- Enumeration preprocesses patterns by removing Ghostscript backslash escapes, tracks directory head length, excludes `.`/`..` and directory entries, and returns full names.
- Cleans up with `FindClose` and Ghostscript memory free calls.
- Implements DOS/Windows path-combine helper functions for roots, separators, parent/current references, and empty item semantics.
- `gp_file_name_combine` delegates to `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Main Win32 filesystem enumeration and path-syntax layer for Ghostscript.

Notable behavior:
- Directory entries are skipped; enumeration is file-oriented.
- If a returned name is too long, it truncates/copies up to `maxlen` and returns `maxlen`.
