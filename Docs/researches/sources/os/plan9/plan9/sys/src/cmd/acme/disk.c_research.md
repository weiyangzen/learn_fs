# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/disk.c

This file provides temporary disk-backed block allocation for Acme buffers.

Key behavior:
- `tempfile()` creates an ORCLOSE/OCEXEC temp file named `/tmp/X?.useracme`.
- `diskinit()` allocates a `Disk` and opens the temp file.
- `ntosize()` rounds a rune count to a block-size bucket.
- `disknewblock()` allocates/reuses a `Block` from size-specific free lists and advances the temp-file address.
- `diskrelease()` returns a block to the proper free bucket.
- `diskwrite()` writes runes to a block, replacing the block if size bucket changes.
- `diskread()` reads runes from a block with full-read checking.

Important details:
- Blocks are metadata records allocated in chunks of 100; payload lives in one temp file.
- Size classes are multiples of `Blockincr` up to `Maxblock`.
- Temp file is removed automatically on close due to `ORCLOSE`.

Filesystem relevance:
- Direct: Acme’s text buffers are disk-backed through a temporary file, reducing memory pressure for large edits.
