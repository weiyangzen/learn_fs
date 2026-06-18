# File Research: sources/os/linux/linux-stable/fs/squashfs/file_direct.c

## Summary
Provides the file data read implementation for `CONFIG_SQUASHFS_FILE_DIRECT`.

## Key APIs
- `squashfs_readpage_block()`.

## Important Behavior
Computes the page-cache range covered by the Squashfs block, tries to lock/grab all pages in that range, builds a direct page actor, and calls `squashfs_read_data()` so the decompressor writes directly into page-cache pages.

On success, it zeroes the tail of the last file page when needed, flushes dcache, marks pages uptodate, unlocks them, and releases all non-target pages. On decompression failure, non-target pages are unlocked and released while the caller handles the target folio.

## Risks
Direct decompression must cope with missing or already-uptodate pages. `page_actor` and backend `alloc_buffer` behavior determine whether missing pages are skipped safely or fail the read.
