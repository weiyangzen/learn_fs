# File Research: sources/os/linux/linux/fs/ext4/inode.c

## Purpose

`fs/ext4/inode.c` is the main ext4 inode implementation. It handles inode checksum calculation, inode eviction, block mapping, buffered write setup/completion, delayed allocation, writeback, DAX writeback, direct-I/O iomap mapping, page invalidation/release, truncate and punch-hole operations, raw inode read/write, inode flag translation, setattr/getattr, journal-mode switching, and mmap page-fault write preparation.

This file is central glue between VFS inode operations, page cache, buffer heads, iomap, JBD2 journaling, ext4 extent/indirect mapping, delayed allocation, inline data, fscrypt, fsverity, DAX, quota, and fast commits.

## Major Responsibilities

### Inode checksums and raw inode updates

- `ext4_inode_csum()` computes the metadata checksum over the raw inode, zeroing checksum fields during calculation.
- `ext4_inode_csum_verify()` validates stored checksum fields when metadata checksums are enabled and creator OS is Linux.
- `ext4_inode_csum_set()` writes low and optional high checksum words into the raw inode.
- `ext4_fill_raw_inode()` serializes VFS/ext4 in-memory inode state into `struct ext4_inode`, including uid/gid/projid, timestamps, flags, size, block pointers, device numbers, generation, version, file ACL, and checksum.
- `ext4_do_update_inode()` writes the serialized inode into the inode-table buffer, updates lazytime neighbors, handles large-file feature enablement, dirties metadata, clears `EXT4_STATE_NEW`, and updates fsync transaction tracking.
- `ext4_mark_iloc_dirty()`, `ext4_reserve_inode_write()`, and `__ext4_mark_inode_dirty()` are the main journal-aware inode dirtying paths.

### Inode lookup and initialization

- `__ext4_get_inode_loc()` maps an inode number to its inode-table block and offset, with inode-table readahead and an optimization that avoids disk I/O if the inode block contains only this in-memory inode.
- `ext4_get_inode_loc()` and `ext4_get_fc_inode_loc()` expose inode-location lookup for normal and fast-commit paths.
- `__ext4_iget()` reads a raw inode, verifies bounds and checksum, loads core fields, validates mode/size/flags/block references, initializes inline data and xattrs, sets file/dir/symlink/special inode operations, and handles stale file handles.
- `check_igot_inode()` validates expected EA-inode/bad-inode conditions.
- `ext4_iget_extra_inode()` checks in-inode xattr layout and discovers inline data.
- `ext4_set_inode_flags()` maps ext4 inode flags to VFS flags such as `S_SYNC`, `S_APPEND`, `S_IMMUTABLE`, `S_DAX`, `S_ENCRYPTED`, `S_CASEFOLD`, and `S_VERITY`.
- `ext4_set_inode_mapping_order()` configures folio order constraints, lowering journal-data inodes to the minimum order.

### Inode lifecycle and eviction

- `ext4_inode_is_fast_symlink()` detects symlinks stored directly in `i_data`.
- `ext4_evict_inode()` handles final inode cleanup. For linked inodes it truncates page cache and clears in-core state. For unlinked inodes it starts a truncate transaction, zeros size, truncates blocks, deletes xattrs, removes orphan records, sets deletion time, frees the inode, and handles error fallback.
- `ext4_begin_ordered_truncate()` coordinates ordered-data truncation with JBD2.
- `ext4_inode_attach_jinode()` lazily allocates and publishes a JBD2 inode wrapper for ordered/journaled data tracking.

### Block mapping

- `ext4_map_blocks()` is the central logical-to-physical mapping function. It consults the extent-status cache, queries extents or indirect blocks, optionally allocates or converts blocks, validates physical block ranges, updates ordered-data tracking, and tracks fast-commit ranges.
- `ext4_map_query_blocks()` and `ext4_map_create_blocks()` split lookup and creation work.
- `ext4_map_query_blocks_next_in_leaf()` extends a cached extent over the next leaf entry when querying last-in-leaf mappings.
- `_ext4_get_block()`, `ext4_get_block()`, and `ext4_get_block_unwritten()` adapt ext4 mapping into buffer-head `get_block_t` callbacks.
- `ext4_getblk()`, `ext4_bread()`, and `ext4_bread_batch()` provide metadata/data buffer access by logical block.
- `check_block_validity()` rejects mappings outside legal filesystem block ranges, except for the journal inode.
- `ext4_issue_zeroout()` zeroes physical ranges, delegating to fscrypt zeroout for encrypted regular files.

### Buffered write path

- `ext4_block_write_begin()` prepares buffer heads for a folio write, maps missing blocks, reads partial existing blocks, zeroes partial new blocks, decrypts read buffers for fs-layer encryption, and handles journal-data write access.
- `ext4_write_begin()` handles non-delalloc buffered writes: emergency-state checks, inline-data attempt, folio allocation before journal start, block mapping, data-journal access, retry on `-EAGAIN`/`-ENOSPC`, and failed-write truncation.
- `ext4_write_end()` completes non-journal buffered writes: commits written bytes, updates `i_size`, marks inode dirty, handles orphan cleanup for short writes beyond EOF, and stops the journal.
- `ext4_journalled_write_end()` completes data-journal writes by dirtying data buffers as metadata, updating `i_datasync_tid`, and handling short writes.
- `ext4_journalled_zero_new_buffers()` zeroes and journals new buffers without relying on generic dirtying.

### Delayed allocation and writeback

- `ext4_da_reserve_space()`, `ext4_da_release_space()`, and `ext4_da_update_reserve_space()` manage per-inode reserved delayed-allocation clusters and quota reservations.
- `ext4_clu_alloc_state()` and `ext4_insert_delayed_blocks()` handle bigalloc-aware delayed reservation accounting.
- `ext4_da_map_blocks()` finds existing mappings or inserts delayed extents into the extent-status tree.
- `ext4_da_get_block_prep()` prepares buffer heads for delayed allocation, marking delayed or unwritten buffers appropriately.
- `ext4_da_write_begin()` chooses delayed allocation unless free space is low or fsverity is writing Merkle data; it also supports inline-data setup.
- `ext4_da_write_end()` and `ext4_da_do_write_end()` finish delayed writes, update `i_size`, and update `i_disksize` only when the end block is already mapped.
- `ext4_alloc_da_blocks()` forces delayed blocks to be allocated by flushing the mapping.
- `ext4_do_writepages()` is the main writeback engine. It handles inline-data destruction before writeback, data-journal mode, dioread_nolock reserved handles, cyclic ranges, dirty-page scanning, block allocation for delayed/unwritten buffers, bio submission, transaction lifetime, error recovery, and writeback index updates.
- `mpage_*` helpers collect dirty folios, build extents to map, map delayed/unwritten buffers, submit bios, update `i_disksize`, release unused pages, and handle fatal writeback errors.
- `ext4_writepages()` wraps `ext4_do_writepages()` with ext4 writepages locking and reruns data-journal writeback if DMA-pinned pages were dirtied behind journaling.
- `ext4_normal_submit_inode_data_buffers()` submits ordered-data dirty ranges for JBD2.
- `ext4_dax_writepages()` delegates DAX writeback to `dax_writeback_mapping_range()`.

### Iomap, DAX, direct I/O, and atomic writes

- `ext4_set_iomap()` converts `ext4_map_blocks` results into iomap records, including mapped, unwritten, delayed, hole, dirty, new, DAX, and atomic-bio flags.
- `ext4_iomap_begin()` is the main iomap begin operation for direct I/O and DAX. It rejects inline data, allocates blocks for writes, limits fscrypt I/O block continuity, and validates atomic-write coverage.
- `ext4_iomap_alloc()` starts journal transactions for direct/DAX writes, chooses create/unwritten/zeroing flags, retries ENOSPC, and forces a commit for mixed atomic-write mappings.
- `ext4_map_blocks_atomic_write()` and `_slow()` ensure atomic-write ranges resolve to one contiguous mapped extent, using bigalloc-only slow-path zeroing for mixed mappings.
- `ext4_iomap_begin_report()` reports mappings for fiemap/swap-like queries and supports inline-data iomap reporting.
- `ext4_iomap_ops` and `ext4_iomap_report_ops` publish iomap operations.
- `ext4_dio_alignment()` reports DIO alignment capability, rejecting fsverity, journal-data, inline-data, and unsupported encrypted files.
- `ext4_iomap_swap_activate()` activates iomap-based swapfiles.

### Address-space operations

The file defines address-space operation tables:

- `ext4_aops`: regular non-delalloc buffered mode.
- `ext4_journalled_aops`: data=journal mode, with journalled write end, dirty folio, invalidate, and migration behavior.
- `ext4_da_aops`: delayed-allocation mode.
- `ext4_dax_aops`: DAX writeback/dirty/bmap/swap operations.

`ext4_set_aops()` chooses the correct table based on inode journal mode, DAX, and delalloc mount options.

### Truncate, zeroing, and hole punching

- `ext4_block_zero_range()`, `ext4_block_do_zero_range()`, and `ext4_block_journalled_zero_range()` zero partial block ranges for normal, DAX, and journal-data modes.
- `ext4_block_zero_eof()` zeroes from EOF to block end and orders zeroed written data before `i_disksize` updates in ordered mode.
- `ext4_zero_partial_blocks()` zeroes partial start/end blocks around a hole-punch or zero range.
- `ext4_can_truncate()` allows truncation for regular files, directories, and non-fast symlinks.
- `ext4_update_disksize_before_punch()` ensures `i_disksize` is updated before page-cache truncation can prevent writeback from doing so.
- `ext4_truncate_page_cache_block_range()` handles page-cache invalidation for punched ranges, including journal-data write-and-wait and partial-folio mmap cleanup.
- `ext4_break_layouts()` coordinates DAX layout breaking.
- `ext4_punch_hole()` zeros partial blocks, removes page cache, starts a truncate transaction, removes extent or indirect mappings, inserts hole status, tracks fast-commit ranges, and handles sync semantics.
- `ext4_truncate()` performs crash-consistent truncate with orphan-list protection, inline-data truncation, EOF zeroing, extent/indirect truncation, timestamp update, and inode dirtying.

### setattr/getattr

- `ext4_setattr()` handles VFS attribute changes. It enforces immutable/append restrictions, prepares fscrypt and quota changes, transfers quota ownership, handles file size changes, converts inline data when new size exceeds inline capacity, waits for DIO on shrink, breaks DAX layouts, zeroes EOF tails on extension, updates `i_size` and `i_disksize` under `i_data_sem`, tracks fast-commit ranges, truncates page cache, calls `ext4_truncate()`, increments inode version, and updates ACLs for mode changes.
- `ext4_getattr()` fills birth time, DIO alignment, atomic-write capability, and user-visible ext4 attribute flags.
- `ext4_file_getattr()` adjusts reported block count for inline data and delayed allocations.

### Journal mode and mmap write faults

- `ext4_change_inode_journal_flag()` safely switches per-inode data journaling. It waits for DIO, flushes and invalidates page cache, locks journal updates and writepages, flushes the journal when disabling data journaling, switches aops, marks fast commits ineligible, and dirties the inode.
- `ext4_page_mkwrite()` handles mmap write faults: starts pagefault protection, updates file time, converts inline data, uses delalloc where possible, verifies folio size/truncation races, avoids journal start when all buffers are already mapped, and otherwise allocates/makes buffers writable via `ext4_block_page_mkwrite()`.
- `ext4_block_page_mkwrite()` starts a write transaction, locks the folio, maps needed blocks, commits buffers, and handles data-journal mode.

## Important Structures and Constants

- `struct mpage_da_data`: state object for writeback scanning, delayed mapping, io submission, and range tracking.
- `DIO_MAX_BLOCKS`: maximum direct-I/O mapping length, 4096 blocks.
- `BH_FLAGS`: buffer state mask for delayed/unwritten writeback collection.
- `MAX_WRITEPAGES_EXTENT_LEN`: caps writeback mapping extent length at 2048 blocks.

## Dependencies and Integration

This file integrates with:

- JBD2 journaling: transaction starts/stops, ordered data lists, data journaling, journal inode tracking, fast commits.
- ext4 extent and indirect mapping: `ext4_ext_map_blocks()`, `ext4_ind_map_blocks()`, truncate/remove/check helpers.
- extent-status cache: lookup, insert, remove, delayed/hole/written/unwritten states.
- page cache and writeback: folios, buffer heads, `write_begin_get_folio()`, `block_write_end()`, `filemap_flush()`, `filemap_write_and_wait*()`.
- iomap and DAX: direct I/O, fiemap reporting, swap activation, DAX writeback and zeroing.
- inline data: calls into `inline.c` for inline write setup, conversion, truncation, and iomap reporting.
- fscrypt/fsverity: encrypted zeroout/decryption/DIO alignment and verity write-size behavior.
- quotas: delayed allocation reservations, ownership transfer, xattr-inode usage.
- VFS inode operations: iget, eviction, setattr/getattr, dirty inode, mmap page faults.

## Locking and Ordering

Key locking patterns:

- `i_data_sem` protects extent/indirect mapping mutations, extent-status updates tied to mapping, and coordinated `i_size`/`i_disksize` updates.
- folio locks protect write begin/end, writeback submission, partial zeroing, and page fault mapping.
- `filemap_invalidate_lock` protects truncate, DAX layout breakage, journal-mode switching, and mmap/page-cache invalidation interactions.
- JBD2 transaction handles wrap all metadata mutations and some data-buffer mutations in journal-data mode.
- orphan-list updates protect crash recovery during truncate and failed over-EOF writes.
- writepages locking (`ext4_writepages_down_read/write`) serializes writeback against mode changes and allocation-sensitive operations.
- raw inode writes use `i_raw_lock` while serializing in-memory fields into the on-disk inode.

## Error Handling and Corruption Checks

Important checks include:

- inode number bounds and special-inode access mode in `__ext4_iget()`;
- raw inode checksum verification, with `-EFSBADCRC` on mismatch;
- invalid `i_extra_isize`, size beyond maxbytes, bad xattr block, bad extent/indirect block references;
- invalid inline-data plus extents flag combination;
- invalid dir-index flag when filesystem lacks `dir_index` under metadata checksums;
- invalid symlink flags or malformed fast symlink length;
- physical block validity checks after mappings;
- delayed allocation fatal errors can force dirty-page invalidation to prevent infinite writeback loops;
- atomic write mapping failures return errors rather than risking torn or discontiguous writes;
- emergency filesystem state short-circuits writes and dirtying.

## Notable Risk Areas

- `ext4_map_blocks()` is a concurrency-sensitive choke point. Incorrect flags or missing locks can corrupt extent-status cache assumptions, especially around `EXT4_GET_BLOCKS_IO_SUBMIT`, `EXT4_EX_NOCACHE`, and writeback callers.
- `i_size` and `i_disksize` ordering is critical. The file repeatedly updates them under `i_data_sem` or folio lock to avoid stale exposure and crash-inconsistent allocation beyond EOF.
- Delayed allocation accounting spans quota reservations, per-inode counters, dirty cluster counters, bigalloc cluster sharing, and extent-status entries.
- Journal-data mode has special folio dirtying semantics. DMA-pinned folios are marked checked and journaled later by writepages.
- Truncate and punch-hole paths rely on orphan records, page-cache invalidation, EOF zeroing, and metadata transaction ordering for recovery correctness.
- Inline data conversion is interleaved with generic write, delayed allocation, truncate, setattr, and page fault paths.
- Atomic-write support adds strict contiguous mapping requirements and forced transaction commits for mixed mappings.
- Journal mode switching is intentionally heavyweight because stale journal records can corrupt data if mode changes are not serialized with writeback and journal flushes.
