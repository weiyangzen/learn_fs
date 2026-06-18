# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.c

## Scope

This file implements Btrfs page-cache I/O helpers for file data plus the in-memory extent-buffer implementation used for metadata tree blocks. It covers data read/readahead, data writeback from delalloc through ordered extents and bios, btree metadata writeback, extent-buffer allocation and lookup in the fs-wide xarray, extent-buffer refcount and folio-private lifetime, metadata block reads, dirty/uptodate state propagation, release/invalidate hooks, and byte/bitmap/memcpy helpers for accessing tree blocks across folio boundaries.

It is the central bridge between Btrfs logical extents, the kernel page cache/folio APIs, bio submission, ordered extents, fsverity, metadata tree locking, subpage state, zoned metadata write ordering, and the extent map cache.

## Main APIs And Entry Points

- `extent_buffer_init_cachep()` and `extent_buffer_free_cachep()` create and destroy the extent-buffer slab cache.
- `btrfs_read_folio()` locks the requested file range, waits or skips ordered extents as appropriate, maps the file offsets through extent maps, and submits read bios.
- `btrfs_readahead()` performs the same read mapping over a readahead window, including compressed extent readahead expansion.
- `btrfs_writepages()` drives buffered data writeback through `extent_write_cache_pages()`, `writepage_delalloc()`, `extent_writepage_io()`, and `submit_one_sector()`.
- `extent_write_locked_range()` submits already-delalloc-processed locked file ranges, used by callers that have pre-created ordered extents.
- `btree_writepages()` writes dirty metadata extent buffers from `fs_info->buffer_tree` xarray tags instead of normal file page-cache dirty tags.
- `btrfs_btree_wait_writeback_range()` waits for metadata extent-buffer writeback over a logical bytenr range.
- `extent_invalidate_folio()`, `try_release_extent_mapping()`, and `try_release_extent_buffer()` are address-space release/invalidate helpers for btree/data folios.
- `alloc_extent_buffer()`, `find_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `free_extent_buffer()`, and `free_extent_buffer_stale()` implement extent-buffer creation, lookup, cloning, and lifetime.
- `read_extent_buffer_pages_nowait()` and `read_extent_buffer_pages()` submit and wait for metadata block reads with parent/key/generation validation.
- `set_extent_buffer_dirty()`, `btrfs_clear_buffer_dirty()`, `set_extent_buffer_uptodate()`, and `clear_extent_buffer_uptodate()` synchronize extent-buffer flags with per-folio or subpage state.
- `read_extent_buffer()`, `write_extent_buffer()`, `copy_extent_buffer()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, `memcmp_extent_buffer()`, `extent_buffer_test_bit()`, `extent_buffer_bitmap_set()`, and `extent_buffer_bitmap_clear()` provide safe tree-block memory access.
- `btrfs_inhibit_eb_writeback()` and `btrfs_uninhibit_all_eb_writeback()` let a transaction temporarily discourage WB_SYNC_NONE metadata writeback for selected extent buffers.
- `btrfs_readahead_tree_block()` and `btrfs_readahead_node_child()` perform nonblocking metadata readahead for tree blocks and node children.

## Control Flow And Behavior

Data read starts by locking the inode `io_tree` range and reconciling any overlapping ordered extents. `lock_extents_for_read()` can skip waiting when the locked folios are already dirty or uptodate in ways that cannot be helped by waiting; otherwise it starts and waits ordered extent completion, then retries. `btrfs_do_readpage()` sets folio-private state, zeros beyond i_size, handles already-uptodate sectors, gets cached extent maps through `get_extent_map()`, and distinguishes holes, inline extents, prealloc-as-hole reads, regular extents, and compressed extents. Regular sectors are merged into bios when file offsets and disk sectors are contiguous; compressed reads are kept grouped by compression type and by extent-map identity to avoid corrupting aliased references to the same compressed physical extent.

Data read endio validates fsverity before setting folio uptodate bits, zeros partial EOF sectors, clears subpage lock state, and releases bios. For data reads older than the current fs generation, bio submission can set `csum_search_commit_root` so checksum lookup can use the commit root.

Data writeback first walks dirty folios with normal writeback indexing and tagging semantics. `writepage_delalloc()` captures the dirty/subpage bitmap, locks delalloc ranges with `find_lock_delalloc_range()`, runs `btrfs_run_delalloc_range()`, and removes asynchronously handled compression/inline ranges from the submission bitmap. `extent_writepage_io()` performs COW fixup, maps each remaining sector through `btrfs_get_extent()`, handles sectors beyond i_size by truncating ordered extents, marks dirty/writeback/ordered bits, and submits bios. Endio clears ordered and writeback bits, sets mapping errors, and completes the ordered extent.

Write bio assembly is managed by `struct btrfs_bio_ctrl`. It tracks the current `btrfs_bio`, next file offset, compression type, ordered extent boundary, writeback control, cgroup ownership, readahead state, and last compressed extent-map start. Data write bios are capped at ordered extent boundaries and initialized with the latest device for cgroup writeback compatibility. Errors before submission finish affected ordered sectors manually so stale dirty bits do not cause later writeback without an ordered extent.

Metadata writeback uses `fs_info->buffer_tree`, an xarray indexed by nodesize units. Dirty extent buffers are tagged with xarray marks; WB_SYNC_ALL first moves dirty marks to TOWRITE. `btree_writepages()` batches tagged EBs, checks zoned metadata write-pointer constraints, locks each EB for I/O, clears DIRTY, sets WRITEBACK, updates dirty metadata accounting, zeroes unused leaf/node regions in `prepare_eb_write()`, builds one metadata bio, and submits it. Metadata write endio clears metadata folio writeback bits, clears the xarray writeback mark, wakes waiters, and records btree/log write errors in fs-wide flags.

Extent buffers are allocated around the btree inode page cache. `alloc_extent_buffer()` validates alignment, handles 32-bit page-cache limits, preallocates subpage folio state when needed, allocates folios, attaches them to the btree inode filemap, reuses existing folios/EBs if races are found, sets lockdep class by owner root and tree level, computes an optional direct `addr` when backing pages are physically contiguous, then inserts into `fs_info->buffer_tree`. The `EXTENT_BUFFER_TREE_REF` bit represents the xarray's reference; `check_buffer_tree_ref()` repairs races before I/O or access paths so release_folio cannot drop the tree reference while new users are active.

Extent-buffer freeing is split between normal and stale paths. `free_extent_buffer()` uses a fast atomic decrement when safely above low refcounts, otherwise takes `refs_lock`. If an EB is stale, has only the tree and caller references, and is not dirty or under writeback, the tree reference can be dropped. The final release removes the xarray entry with cmpxchg, detaches folio-private state, and frees through RCU unless it is an unmapped test/dummy buffer.

Metadata reads use `EXTENT_BUFFER_READING` to serialize concurrent reads. If the EB is already uptodate, `btrfs_buffer_uptodate()` validates it against the requested parent check. Otherwise `read_extent_buffer_pages_nowait()` sets READING, takes a ref for endio, builds a metadata read bio over all EB folios, and submits it. Endio records the mirror, validates the tree block via `btrfs_validate_extent_buffer()`, sets or clears uptodate state, clears READING, drops the EB ref, and releases the bio.

The byte access helpers hide whether an EB is backed by one contiguous virtual address, multiple page-sized folios, or a subpage-positioned metadata block. All public read/write/copy helpers validate the EB-relative range before touching memory. Bitmap operations intentionally operate with byte granularity because on-disk bitmap items are little-endian and may straddle page boundaries.

## State And Data Structures

- `struct btrfs_bio_ctrl` carries in-progress data bio state, compression mode, ordered extent boundary, csum generation optimization, writeback control, submit bitmap, readahead control, and compressed extent-map identity.
- `struct extent_buffer` fields managed here include logical `start`, `len`, `folio_size`, `folio_shift`, `addr`, `bflags`, `refs`, `refs_lock`, `writeback_inhibitors`, `log_index`, `read_mirror`, `lock`, folio array, and debug leak list.
- Extent-buffer flags include UPTODATE, DIRTY, TREE_REF, STALE, WRITEBACK, UNMAPPED, WRITE_ERR, ZONED_ZEROOUT, and READING.
- Per-folio Btrfs subpage/private state tracks data dirty/lock/ordered/writeback/uptodate bits and metadata EB refs/dirty/writeback/uptodate bits.
- `fs_info->buffer_tree` is the xarray of live metadata EBs, with PAGECACHE_TAG_DIRTY, PAGECACHE_TAG_WRITEBACK, and PAGECACHE_TAG_TOWRITE marks.
- `fs_info->dirty_metadata_bytes`, fs error flags, log write error flags, zoned metadata state, and transaction writeback inhibition xarrays are updated here.

## Dependencies

- Extent state and delalloc helpers from `extent-io-tree.c`.
- Extent maps from `extent_map.c` and `btrfs_get_extent()`.
- Ordered extent lifecycle, delalloc running, compression, inline extent handling, and COW fixup from inode/file code.
- Bio allocation/submission and checksum handling from `bio.c` and file-item checksum code.
- Metadata validation and tree parent checks from disk I/O/tree-checking paths.
- Subpage state helpers, zoned metadata/data relocation locks, block-group write pointer checks, fsverity, writeback control, cgroup writeback accounting, and kernel folio/page-cache APIs.

## Risks And Invariants

- Read paths must hold the inode extent lock while getting a stable view of extent maps and ordered extents; otherwise reads can race ordered extent completion and observe stale or missing file extent items.
- Compressed reads cannot be merged solely by physical bytenr. Different file ranges can reference the same compressed extent with different offsets, so the code forces bio splits by extent-map start.
- Delalloc writeback must either submit every created ordered range or explicitly mark it finished on error. Leaving dirty bits without an ordered extent can cause later writeback corruption.
- Subpage filesystems require per-sector dirty, ordered, writeback, lock, and uptodate accounting; full-folio flags alone are insufficient.
- Metadata write errors must be recorded outside the EB itself, because the EB may be released before transaction commit detects the error.
- Extent-buffer `TREE_REF` handling is race-sensitive. It is the xarray reference, and release_folio may clear it only when the EB is otherwise unreferenced and not under I/O.
- Folio private state for metadata must be changed under `mapping->i_private_lock` when the EB is mapped in the btree inode.
- `EXTENT_BUFFER_READING` must not be cleared after setting UPTODATE too early; other readers can otherwise return without waiting for validation and I/O completion.
- Zoned metadata writeback relies on serialized write-pointer checks and `meta_write_pointer` advancement before submission.
- Bitmap helpers must preserve byte-order and cross-page behavior; replacing them with word operations would break on-disk bitmap format assumptions.
