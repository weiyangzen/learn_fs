# File Research: sources/os/linux/linux-stable/fs/nilfs2/alloc.c

Purpose: implements NILFS2’s persistent object allocator used for metadata objects such as DAT entries and disk inodes. It manages grouped descriptor blocks, bitmap blocks, and entry blocks in NILFS metadata files.

Key structures and state:
- Allocator geometry derives from metadata-file block size: entries per group, groups per descriptor block, blocks per group, and blocks per descriptor block.
- Uses `struct nilfs_palloc_group_desc` on disk to track free-entry counts per group.
- Uses bitmap blocks for allocation state and entry blocks for the actual persistent records.
- `struct nilfs_palloc_req` carries allocation/free transaction state: entry number plus held descriptor, bitmap, and entry buffers.
- `struct nilfs_palloc_cache` stores last-used descriptor, bitmap, and entry buffer heads behind a spinlock.

Major logic:
- `nilfs_palloc_init_blockgroup()` allocates block-group locks, sets metadata entry sizing, and computes per-group/per-descriptor geometry.
- Block-offset helpers map an entry number to group number, descriptor block, bitmap block, and entry block.
- `nilfs_palloc_get_block()` provides cached metadata block lookup/creation with optional block initialization and safe cache replacement.
- Descriptor blocks are initialized so each group starts with all entries free.
- Allocation scans descriptor groups from a target entry, optionally wraps, skips full groups, maps bitmap blocks, atomically sets a free bit, decrements descriptor free count, and returns held buffers for commit/abort.
- Commit allocation marks bitmap/descriptor buffers dirty, marks the metadata file dirty, and releases buffers.
- Commit/abort free and abort allocation clear bitmap bits atomically, warn on double-free, adjust descriptor free counts, and release buffers.
- `nilfs_palloc_freev()` bulk-frees sorted entries by group, clears bits, detects empty entry blocks for deletion, updates group free counts, deletes bitmap blocks when a group becomes fully free, and logs cleanup warnings.
- `nilfs_palloc_count_max_entries()` derives maximum describable entries from existing descriptor blocks, with growth allowance when current usage exactly reaches capacity.
- Cache setup/clear/destroy install and release last-buffer references.

Concurrency and lifetime:
- Per-cache spinlock protects cached buffer-head pointers.
- Per-group block-group locks protect descriptor free counts and bitmap bit operations.
- Buffer heads acquired in prepare calls are intentionally retained in request structs until commit or abort.
- Folio mappings use `kmap_local_folio()`/`kunmap_local()` around descriptor/bitmap mutation.
- Metadata buffers are marked dirty and the metadata inode is marked dirty only on committed changes.

Important dependencies:
- Uses NILFS metadata-file APIs from `mdt.h`, bmap lookup for descriptor counts, and ext2-style atomic little-endian bit operations.
- Supplies allocation services consumed by DAT, ifile, and bmap pointer-management helpers.

Risk/edge cases:
- Double-free or aborting an already freed entry is detected by bitmap clear failure and logged as a warning.
- Empty entry/bitmap block deletion failures are warned but nonfatal for `-ENOENT`.
- Descriptor-count logic can return `-ERANGE` if recorded used entries exceed describable capacity.
- The code notes descriptor block initialization does not support block size greater than page size.
