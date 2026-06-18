# File Research: sources/os/linux/linux-stable/fs/affs/file.c

This file implements AFFS regular-file I/O, block mapping, extension block caching, OFS data-block handling, truncation, preallocation cleanup, and fsync.

Major responsibilities:
- Tracks open count and on last close truncates pending size changes and frees preallocated blocks.
- Maps logical file blocks to AFFS data block numbers through header/extension block tables.
- Allocates and links extension blocks as files grow beyond the block pointer capacity of a single header block.
- Provides normal FFS address-space operations using Linux block helpers.
- Provides OFS-specific address-space operations because OFS stores a data header before each payload.
- Clears the Amiga archived bit on file writes.
- Frees file blocks and extension blocks during shrink/truncate and inode eviction.

Extension block cache:
- `i_ext_bh`/`i_ext_last` cache the last extension block.
- A linear cache `i_lc` stores every Nth extension block key.
- An associative cache `i_ac` stores recently used extension keys.
- `affs_grow_extcache()` allocates and resizes cache density as `i_extcnt` grows.
- `affs_get_extblock_slow()` handles sequential access, cache lookup, fallback chain walking, and extension block allocation.

FFS block mapping:
- `affs_get_block()` validates requested logical blocks, locks the extension cache, locates the extension block, maps an existing data block, and optionally allocates exactly the next block.
- New block allocation updates `mmu_private`, `i_blkcnt`, block pointer table, block count, first-data pointer, checksum, and inode dirty state.
- Direct I/O refuses extending writes beyond `mmu_private`, falling back to buffered allocation.

OFS data handling:
- OFS data blocks have `struct affs_data_head`, so file payload size is `s_data_blksize`, not raw block size.
- `affs_do_read_folio_ofs()` copies payload bytes from AFFS data areas into folios.
- `affs_extent_file_ofs()` fills holes by allocating OFS data blocks, setting headers, zeroing partial tails, and linking `next` pointers.
- `affs_write_begin_ofs()` extends files before writes when needed and ensures folios are fully populated for short-write safety.
- `affs_write_end_ofs()` writes payload into OFS blocks, initializes new data headers, updates per-block size and next links, fixes checksums, and updates file size.

Truncation:
- Growing a file delegates through the mapping write path to allocate or zero the target range.
- Shrinking clears extension caches beyond the retained extension, frees excess data blocks, clears block pointers, fixes checksums, updates `i_blkcnt`/`i_extcnt`, and frees extension blocks in the old tail chain.
- OFS truncation also clears the last retained data block’s `next` pointer.
- Preallocated blocks are always released after truncation.

Synchronization:
- Metadata buffer heads modified by this file are tracked in `i_metadata_bhs`.
- `affs_file_fsync()` waits for writeback, writes the inode synchronously, and syncs the underlying block device.
