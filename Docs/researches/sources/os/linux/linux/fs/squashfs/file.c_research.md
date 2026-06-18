# File Research: sources/os/linux/linux/fs/squashfs/file.c

Implements regular-file read, readahead, sparse-block handling, fragment-tail handling, and `SEEK_DATA`/`SEEK_HOLE`.

SquashFS stores per-file compressed block sizes in inode metadata. For large files, this file maintains a small meta-index cache mapping logical block indexes to block-list and data-block positions, avoiding repeated linear scans.

`read_blocklist_ptrs()` locates a block-list entry and returns compressed size plus disk position. `squashfs_read_folio()` chooses between sparse zero fill, full datablock read, or fragment-tail read.

`readahead` expands requests to SquashFS block boundaries and decompresses directly into page batches where possible. `seek_hole_data()` scans block-list entries to report sparse regions.

Exports `squashfs_aops` and `squashfs_file_operations`.
