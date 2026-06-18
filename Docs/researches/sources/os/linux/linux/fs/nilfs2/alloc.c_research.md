# File Research: sources/os/linux/linux/fs/nilfs2/alloc.c

`alloc.c` implements NILFS2’s persistent object allocator used for DAT entries and disk inode allocation. It manages grouped metadata files consisting of descriptor blocks, bitmap blocks, and entry blocks.

Core layout helpers:
- `nilfs_palloc_entries_per_group()` is defined in the header; this file adds group count, groups per descriptor block, group/offset calculation, descriptor block offset, bitmap block offset, and entry block offset.
- `nilfs_palloc_init_blockgroup()` allocates block-group locks, configures metadata entry size, computes blocks per group, and computes blocks per descriptor block.
- Descriptor initialization fills each group descriptor’s free-entry count.

Buffer/cache handling:
- `nilfs_palloc_get_block()` caches the last descriptor, bitmap, and entry block through `nilfs_palloc_cache`, protected by a spinlock.
- Delete helpers invalidate matching cached buffers before deleting metadata blocks.
- Public `nilfs_palloc_get_entry_block()` locates an entry’s data block.
- Offset helpers compute descriptor, bitmap, and entry byte offsets within folios.

Allocation flow:
- `nilfs_palloc_prepare_alloc_entry()` scans descriptor blocks and group bitmaps from the requested entry number, optionally wrapping, atomically sets a free bit, decrements descriptor free count, and returns pinned descriptor/bitmap buffers in `nilfs_palloc_req`.
- `nilfs_palloc_commit_alloc_entry()` dirties descriptor/bitmap buffers, marks the metadata inode dirty, and releases buffers.
- `nilfs_palloc_abort_alloc_entry()` clears the allocated bit, increments free count, releases buffers, and resets request fields.

Free flow:
- `nilfs_palloc_prepare_free_entry()` pins descriptor and bitmap buffers for an entry.
- `nilfs_palloc_commit_free_entry()` clears the bit atomically, warns if already free, increments the descriptor free count, dirties buffers, marks metadata dirty, and releases buffers.
- `nilfs_palloc_abort_free_entry()` releases buffers without changing bitmap state.
- `nilfs_palloc_freev()` batch-frees sorted entries, deletes now-empty entry blocks, updates descriptor free counts, and deletes empty bitmap blocks when an entire group becomes free.

Capacity/cache:
- `nilfs_palloc_count_max_entries()` derives maximum allocatable entries from current descriptor blocks and possible metadata growth.
- Setup/clear/destroy cache functions attach and release the per-inode allocator cache.

Important risks/semantics: allocation is a prepare/commit/abort protocol; callers must complete the transaction correctly. Bitmap mutation uses ext2 little-endian atomic bit operations, while descriptor free counts are protected by per-group locks.
