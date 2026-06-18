# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass5.c

This file implements phase 5: cylinder group and summary reconstruction.

Key behavior:
- Builds a fresh `struct cg` image for each cylinder group from pass-derived inode/block state.
- Handles conversion-level updates for clustering maps.
- Optionally rewrites cylinder groups to add check hashes.
- Recomputes inode-used maps, block-free maps, fragment summaries, cluster maps, and cylinder group summaries.
- Optionally zeroes or deletes unallocated fragments when `-Z` or `-E` is used.
- Compares rebuilt per-cg summaries against superblock summaries and repairs when approved.
- Compares rebuilt cylinder-group headers/maps against on-disk versions and repairs when approved.
- Accumulates total filesystem summary and repairs `fs_cstotal`.
- In background/snapshot mode, adjusts live superblock summaries through sysctl operations instead of writing snapshot metadata.

`update_maps()` and `check_maps()`:
- Compare claimed allocation maps against computed maps.
- Report allocated resources marked free.
- Free resources marked used but determined unallocated, using sysctls in background mode.
- Separates directory and file inode freeing to account for directory count differences.

`clear_blocks()`:
- Performs zeroing through `blzero()` and delete/TRIM through `blerase()` for contiguous free fragment ranges.

Important interactions:
- Relies on `blockmap`, `inostathead`, and counters built by earlier passes.
- Uses `dofix()` to share preen/manual repair policy.
- Must run after `snapflush()` so snapshot COW allocations are reflected before rebuilding maps.
