# File Research: sources/os/linux/linux/fs/squashfs/file_direct.c

Implements direct decompression into page-cache pages.

It gathers all pages covered by the SquashFS block, skipping already-uptodate pages, creates a special page actor, and calls `squashfs_read_data()` so the decompressor writes into page mappings.

On success it zeroes trailing bytes on the final file page, flushes dcache, marks pages uptodate, unlocks them, and releases non-target pages.

On failure it leaves the caller’s target folio for the caller to finish and unlocks/releases the other grabbed pages.
