# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.c

## Purpose
Implements `e2freefrag`, a free-space fragmentation reporter for ext2/3/4 filesystems. It can also be compiled into `debugfs` as `do_freefrag`.

## Main Behaviors
- Parses `-c` chunk size in KB and validates power-of-two and block-size constraints.
- Opens the filesystem read-only through ext2fs unless compiled for `debugfs`.
- Collects free extent statistics via:
  - Online FSMAP ioctl scanning when available and the filesystem is mounted.
  - Offline ext2 block bitmap scanning as fallback.
- Reports totals, chunk stats, min/max/average free extent size, number of free extents, and a histogram.

## Important Functions
- `init_chunk_info`: initializes chunk size, block counts, histogram state, and min/max/avg fields.
- `update_chunk_stats`: updates histogram and aggregate free extent metrics.
- `scan_block_bitmap`: offline bitmap scan over blocks/clusters to identify contiguous free runs and aligned chunks.
- `scan_online`: optional live scan using `FS_IOC_GETFSMAP` and `FMR_OWN_FREE`.
- `scan_offline`: reads block bitmap and calls `scan_block_bitmap`.
- `dump_chunk_info`: formats all output.
- `collect_info`: coordinates scanning and output.
- `open_device` / `close_device`: standalone open/close wrappers.
- `do_freefrag` / `main`: shared command entry depending on `DEBUGFS`.

## Dependencies
- `ext2fs` block bitmap and filesystem APIs.
- Optional Linux FSMAP ioctl support through `fsmap.h`.
- `e2freefrag.h` for `struct chunk_info`, histogram constants, and default chunk size.

## Notes and Edge Cases
- The online scan only runs for mounted filesystems and returns false on mount/open/ioctl failure, causing offline fallback where possible.
- Free blocks from online mode are accumulated from free extents rather than the superblock.
- Bigalloc is handled indirectly through ext2fs bitmap behavior; the scanner tests the block map using cluster ratio bits.
