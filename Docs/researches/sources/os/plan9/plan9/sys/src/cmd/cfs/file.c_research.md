# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/file.c

This file implements cached file data reads and writes on top of `Icache` and `Disk`.

Key behavior:
- `fmerge()` merges newly cached bytes into a cached block’s valid byte range.
- `fbwrite()` writes one file block worth of data, allocating direct or indirect data blocks and preserving write ordering.
- `fwrite()` writes arbitrary byte ranges by splitting them into cache-block chunks.
- `fpget()` finds the next valid cached data pointer at or after a file offset.
- `fread()` reads cached data, returning:
  - positive bytes read when data is present,
  - negative gap size when the first requested range is missing,
  - zero when no cached data is available.

Important details:
- Each cached disk block tracks one valid byte range.
- Direct pointers are converted to indirect blocks when multiple file-block positions need to be cached.
- `fread()`’s negative gap return is the mechanism `cfs.c` uses to ask the server only for missing ranges.

Filesystem relevance:
- Direct. Implements the cached regular-file data layer for `cfs`.
