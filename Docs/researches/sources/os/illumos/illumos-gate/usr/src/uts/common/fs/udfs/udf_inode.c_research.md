# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_inode.c

## Purpose

Implements UDFS inode cache management, on-disk file-entry parsing, inode writeback, allocation-descriptor serialization, truncation, permission checks, timestamp marking, inactive handling, and global inode/free-list initialization.

## Main Entry Points

- `ud_iget()`: lookup or allocate an in-core inode for a partition/reference block, read and decode its UDF file entry, and initialize the vnode.
- `ud_iinactive()`: handle last vnode release, write or delete unlinked files, place reusable inodes on the free list, or destroy excess inodes.
- `ud_iupdat()`: write dirty inode state and allocation descriptors back into the UDF file entry.
- `ud_updat_ext4()`: serialize in-core extents into short/long descriptors and continuation descriptor blocks.
- `ud_itrunc()`, `ud_trunc_ext4()`, `ud_trunc_ext4096()`: implement file growth/shrink and free truncated blocks/continuation descriptors.
- `ud_iflush()`: invalidate cached inodes for unmount.
- `ud_iaccess()`: enforce read-only and mode/privilege checks.
- `ud_imark()`, `ud_itimes_nolock()`: update access/modify/change timestamps and dirty flags.
- `ud_add_to_free_list()`, `ud_remove_from_free_list()`, `ud_init_inodes()`: maintain global inode cache and free-list structures.

## Control Flow And State

`ud_iget()` first searches the hash table under `ud_icache_lock`. On a miss, it reuses an inode from `udf_ifreeh` when possible or allocates a new `ud_inode`/vnode pair, invalidating pages before reuse. It inserts the inode into the hash, reads the file entry, verifies tags, follows strategy-4096 indirect entries to the latest file entry, decodes UID/GID/defaults, mode bits, timestamps, link count, file size, logical blocks recorded, device extended attributes, allocation strategy, descriptor type, and file type.

Allocation descriptors are converted into `i_ext` arrays for short or long descriptors. Continuation descriptors are stored in `i_con` and expanded lazily by the block-mapping layer. Embedded data (`ICB_FLAG_ONE_AD`) records `i_data_off`/`i_max_emb` and uses the file entry body rather than external extents. Invalid descriptors or unsupported allocation types route to `error_ret`, remove the bad inode from hash chains, mark it unusable, and put it on the free list.

`ud_iupdat()` reads the file entry block, marks timestamps, clears dirty flags, writes inode metadata, updates ICB flags and implementation ID, serializes embedded data length or extent descriptors, zero-fills unused descriptor space, retags the file entry, and either synchronously writes or delayed-writes while recording `IBDWRITE`. `ud_updat_ext4()` writes as many descriptors as fit in the file entry, then writes chained allocation extent descriptors and frees unused continuation blocks.

Truncation grows through `ud_bmap_write()` when extending and uses VM page invalidation/zeroing when shrinking. `ud_trunc_ext4()` shortens the containing extent, updates `i_size` and `i_lbr`, writes the inode before freeing old blocks, then frees trailing data and no-longer-needed continuation extents.

## Dependencies

Depends on vnode operations, DNLC purge, page cache APIs, UDF descriptor/tag helpers, allocation/free-space routines, block mapping, timestamp conversion, extended attribute structures for device nodes, and global UDFS mount lists/locks declared across the UDFS implementation.

## Risks

This file owns several delicate lifetime transitions: vnode holds versus free-list membership, pageout races during inode reuse, forced unmount destruction, and unlinked-file deletion. Strategy 4096 is readable enough to find the latest file entry, but `ud_updat_ext4096()` returns `ENXIO`, so writable support is effectively absent for that strategy. Descriptor serialization and truncation must keep `i_lbr`, continuation-block accounting, and free-space state synchronized.
