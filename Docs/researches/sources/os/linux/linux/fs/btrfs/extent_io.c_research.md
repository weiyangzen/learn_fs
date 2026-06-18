# File Research: sources/os/linux/linux/fs/btrfs/extent_io.c

Read completely: 4695 lines.

This file implements Btrfs page-cache/folio I/O helpers and the in-memory `extent_buffer` layer used for metadata blocks. It covers data read/write bio construction, delayed allocation writeback, btree metadata writeback/readback, extent buffer allocation and lifetime, extent-buffer memory access primitives, bitmap helpers, release/invalidation paths, and tree-block readahead.

Core data I/O responsibilities:
- Builds and submits `btrfs_bio` instances through `btrfs_bio_ctrl`, tracking compression type, ordered-extent boundaries, writeback control, file offsets, and extent-map generations.
- Reads data folios with `btrfs_read_folio()` and `btrfs_readahead()`, locking the inode io-tree range first so extent maps are stable against ordered extent completion.
- Handles holes, inline extents, prealloc-as-hole reads, compressed reads, fsverity verification, EOF zeroing, subpage lock/uptodate bits, and checksum lookup optimization via `csum_search_commit_root`.
- Writes dirty folios through `btrfs_writepages()`, `extent_write_cache_pages()`, `extent_writepage()`, `writepage_delalloc()`, and `extent_writepage_io()`.
- Runs delalloc ranges, creates ordered extents, handles async compression/inline submission, truncation past `i_size`, COW fixups, writeback accounting, and final ordered extent completion.
- Provides `extent_write_locked_range()` for call sites that already ran delalloc and hold locked pages.

Core metadata I/O responsibilities:
- Maintains `extent_buffer` objects for btree blocks, backed by folios and indexed by `fs_info->buffer_tree`.
- Implements metadata writeback through `btree_writepages()`, `lock_extent_buffer_for_io()`, `write_one_eb()`, and `end_bbio_meta_write()`.
- Marks dirty/writeback xarray tags, updates `dirty_metadata_bytes`, observes zoned metadata write-pointer ordering, and records transaction/log-tree write errors.
- Implements metadata read through `read_extent_buffer_pages_nowait()`, `read_extent_buffer_pages()`, and `end_bbio_meta_read()`, including parent checks and buffer validation.

Extent buffer lifetime and lookup:
- Creates the `btrfs_extent_buffer` slab cache at init/exit.
- Allocates normal, dummy, cloned, and test extent buffers.
- Attaches extent-buffer folios to the btree inode filemap, including subpage metadata state sharing and private-state reference tracking.
- Uses xarray compare/exchange plus `EXTENT_BUFFER_TREE_REF`, RCU freeing, refcounts, `refs_lock`, and stale/writeback flags to handle races between lookup, release, writeback, and page reclaim.
- Provides `find_extent_buffer()`, `alloc_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, and `try_release_extent_buffer()`.
- Provides transaction-scoped writeback inhibition for extent buffers through `btrfs_inhibit_eb_writeback()` and `btrfs_uninhibit_all_eb_writeback()`.

Extent buffer memory helpers:
- Provides checked reads/writes/copies over extent buffers that may span multiple folios.
- Supports fast direct access through `eb->addr` when folios are physically contiguous.
- Implements `read_extent_buffer()`, `read_extent_buffer_to_user_nofault()`, `write_extent_buffer()`, `copy_extent_buffer_full()`, `copy_extent_buffer()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, and `memcmp_extent_buffer()`.
- Implements byte-granular bitmap set/clear/test for Btrfs bitmap items, avoiding word alignment and endian assumptions.

Important interactions:
- Depends on `extent-io-tree` state bits for delalloc, locking, ordered completion, nodatasum, qgroup reservation, and release decisions.
- Depends on `extent_map` lookup for mapping logical file offsets to disk bytenrs, holes, inline extents, prealloc extents, and compressed extents.
- Coordinates with ordered extents, compression, fsverity, csum lookup, inode writeback control, zoned block groups, btree validation, backrefs, transaction state, and the kernel folio/page-cache APIs.
- Uses Btrfs subpage helpers extensively when sectorsize or nodesize is smaller than `PAGE_SIZE`.

Risk and correctness notes:
- This is concurrency-critical code. Correctness relies on careful lock ordering between folio locks, io-tree locks, extent-map tree locks, xarray locks, btree locks, `refs_lock`, and RCU.
- The read path deliberately waits for or skips ordered extents based on folio dirty/uptodate state; mistakes here can expose stale data or miss checksums.
- The write path has many partial-folio/subpage cases where dirty, ordered, writeback, lock, and error bits must stay aligned by sector.
- Metadata write errors are escalated to filesystem/log-tree error flags to prevent committing invalid btree roots.
- Extent-buffer release is intentionally conservative around stale buffers, tree refs, dirty/writeback state, and subpage shared folios.
- Range checks in extent-buffer memory access warn and avoid copying out-of-range data; callers still depend on valid Btrfs item offsets.
