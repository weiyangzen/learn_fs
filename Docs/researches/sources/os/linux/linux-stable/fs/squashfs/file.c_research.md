# File Research: sources/os/linux/linux-stable/fs/squashfs/file.c

## Summary
Implements regular-file reading, large-file block-list indexing, readahead, sparse block handling, fragment tails, and `SEEK_DATA`/`SEEK_HOLE` for Squashfs.

## Key APIs
- `squashfs_copy_cache()`.
- `squashfs_aops`.
- `squashfs_file_operations`.

## Important Behavior
Regular files are represented by a block list of compressed-size entries plus an optional fragment tail. `read_blocklist_ptrs()` maps a logical block index to the on-disk compressed block and size. A zero block size means a sparse hole.

Large files use an in-memory meta-index cache with 8 slots. `fill_meta_index()` stores coarse mappings from logical block ranges to block-list metadata positions and data-block offsets, reducing repeated scans of long block lists.

`squashfs_read_folio()` chooses between sparse zero-fill, separately compressed data block, or fragment tail. `squashfs_copy_cache()` copies one decompressed Squashfs data block into every page-cache folio it covers and marks each folio uptodate only when the expected bytes were copied.

`squashfs_readahead()` expands readahead to Squashfs block boundaries, batches page-cache pages, and decompresses either a full data block or a fragment directly into the page actor.

`seek_hole_data()` scans block-list entries and treats sparse zero-length blocks as holes, nonzero blocks as data, and fragment tails as data with an implicit hole at EOF.

## Synchronization
The meta-index cache uses `msblk->meta_index_mutex` and per-slot `locked` flags so a slot is not reused while a reader is extending or consuming it.

## Risks
The block-list and meta-index code is sensitive to corrupted size entries and integer scaling between page indexes, Squashfs block indexes, and metadata offsets. Readahead must unlock and put every page on every path.
