# File Research: sources/os/linux/linux/fs/btrfs/inode.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8840, source bytes 262084, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_btrfs_inode_c_1_1_8840_067e97753d47_research.md`
- chunk 2: lines 8841-10805, source bytes 56053, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_btrfs_inode_c_2_8841_10805_04b43d528a11_research.md`

## Chunk Research

### Chunk 1: lines 1-8840

# Chunk Research: sources/os/linux/linux/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/os/linux/linux/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans Btrfs inode support from includes and local helper state through checksum diagnostics, buffered writeback/delalloc, COW/NOCOW/compression decisions, ordered extent completion, delayed iput and orphan cleanup, inode load/update, namespace operations, truncation/expansion, eviction, lookup/readdir, new inode creation, extent lookup, folio invalidation, inode cache lifecycle, getattr, and most rename logic. The chunk stops immediately before `btrfs_rename2()` at line 8841.

## Public And Internal APIs Covered

- Lock wrappers: `btrfs_inode_lock()` and `btrfs_inode_unlock()` combine VFS inode `i_rwsem` locking with Btrfs flags for shared, trylock, and mmap write locking.
- Writeback and delalloc entry points: `btrfs_run_delalloc_range()`, `btrfs_set_extent_delalloc()`, `btrfs_writepage_cow_fixup()`, `btrfs_finish_ordered_io()`, and `btrfs_finish_one_ordered()`.
- Extent mapping APIs: `btrfs_get_extent_allocation_hint()`, `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, `btrfs_truncate_block()`, and `btrfs_cont_expand()`.
- Checksum APIs: `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()`.
- Inode lifecycle APIs: `btrfs_iget()`, `btrfs_iget_path()`, `btrfs_alloc_inode()`, `btrfs_destroy_inode()`, `btrfs_drop_inode()`, and `btrfs_evict_inode()`.
- Namespace operations: lookup, unlink, rmdir, create, mknod, mkdir, hardlink, subvolume deletion, rename exchange, and normal rename.

## Control Flow And Behavior

- `btrfs_run_delalloc_range()` dispatches buffered writeback. It tries inline extent creation, then NOCOW/prealloc writeback, then async compression, and finally regular COW. Zoned filesystems use a path that allocates and immediately writes locked ranges.
- Inline writeback validates strict constraints: offset zero, small enough for sector/page/max-inline limits, whole-file coverage, and not encrypted. It may compress one sector, drop overlapping extents, insert an inline file extent, update inode bytes and `disk_i_size`, and return `1` to fall back to normal extent writeback.
- Async compression uses `async_cow`, `async_chunk`, and `async_extent`. Compression work clears dirty state, compresses chunks, rejects compression unless it saves space, and later submits compressed bios or falls back to uncompressed COW.
- Regular COW reserves data extents, locks file ranges, creates pinned IO extent maps, allocates ordered extents, clones relocation checksums when needed, and clears delalloc state.
- NOCOW scans file extent items and rejects unsafe targets: inline, shared, snapshotted, csum-bearing, compressed, encrypted, encoded, explicit-hole, or readonly extents. Unsafe gaps are coalesced and sent through COW fallback.
- Ordered extent completion persists writeback results: handles IO errors, zoned completion, truncation, transactions, RAID stripe-tree records, NOCOW inode updates, prealloc conversion, COW file extent insertion, checksum insertion, inode byte updates, reservation cleanup, and ordered extent reference removal.
- Orphan cleanup walks orphan items, handles dead roots, fsverity metadata, historical truncate orphan items, and inode reuse, relying on eviction-triggered `iput()` for real unlink cleanup.
- Inode loading fills VFS/Btrfs inode state from btree or delayed inode state, marks pessimistic fsync state after reload, initializes extent tracking, selects operation tables, and inserts the inode into the root xarray.
- Namespace operations update dir items, dir indexes, inode/root refs, link counts, parent sizes, timestamps, inode versions, tree-log delete records, and orphan items.
- Truncation/expansion zero partial EOF blocks, insert holes unless `NO_HOLES`, update extent maps, wait ordered extents, drop file extent items, and mark full fsync when extents were removed.
- Folio release/invalidation waits writeback and subpage spinlock users, accounts ordered extents that will never be submitted, frees qgroup reservations, and avoids clearing extent state still needed by ordered completion.

## State And Data Structures

- Per-inode state includes `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, `disk_i_size`, `dir_index`, `index_cnt`, runtime flags, compression properties, delayed node/iput membership, and root pointer.
- Per-root/fs state includes `root->inodes`, delalloc inode/root lists, async delalloc counters, delayed iputs, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, block reservations, qgroup reservations, and worker queues.
- Key extent flags include `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_FINISHING_ORDERED`, and `EXTENT_NODATASUM`.
- Ordered extent flags distinguish regular COW, NOCOW, prealloc, compressed, direct, encoded, truncated, and IO-error states.
- Btree item types manipulated include inode items, inode refs/extrefs, dir items, dir index items, file extent items, hole extents, orphan items, root refs/backrefs, root items, UUID-tree entries, checksum items, and RAID stripe-tree extent records.

## Dependencies

- VFS/MM: inode/dentry/file ops, folios, address-space ops, page cache, `i_rwsem`, `i_mmap_lock`, truncate helpers, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACLs, fscrypt, LSM xattrs, fsverity cleanup, migration hooks, and whiteout support.
- Btrfs subsystems: transactions, delayed inode/items, ordered data, extent maps, extent I/O, compression, qgroups, relocation/backrefs, root tree, dir/file/inode items, tree log, UUID tree, orphan items, block groups, zoned allocator, RAID stripe tree, verity, subpage state, and property inheritance.
- External users continue outside this chunk: writeback and extent lookup from extent I/O, checksum validation from bio handling, ordered completion from ordered-data code, and NOCOW/IO extent setup from file/direct/encoded write paths.

## Risks And Invariants

- Reservation ownership is the highest-risk area: data space, metadata, qgroup reservations, block-group delalloc bytes, inode bytes, and ordered extent refs are split across multiple phases.
- Error paths must clear only the flags they own; several paths intentionally leave accounting for ordered extent completion or reserved-extent cleanup.
- Lock ordering is fragile: extent locks precede transaction joins in ordered completion; btree paths are released before long operations; delayed iput locking is IRQ-safe; `subvol_sem` serializes subvolume deletion/rename with snapshot operations.
- Fsync/log replay correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning during rename/exchange, and forced full commits for root entries.
- NOCOW must stay conservative or it can write into shared data or leave stale checksums.
- Subpage/blocksize mismatches are explicitly handled in checksum, truncate, invalidate, release, and folio dirty/ordered logic.

## Cross-Chunk References

- This chunk ends immediately before `btrfs_rename2()` at line 8841.
- Later same-file code wires rename helpers into VFS operations and continues with delalloc root flushing, symlink creation, preallocation/fallocate, permission/tmpfile handling, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and operation tables.
- `btrfs_update_inode_bytes()` and `btrfs_assert_inode_range_clean()` are referenced here but defined later.
- `btrfs_find_first_inode()` is called by subvolume deletion pruning here and defined later.
- `btrfs_file_operations` is assigned here but defined elsewhere; `btrfs_aops` and inode operation tables are declared in this chunk and defined after the boundary.

### Chunk 2: lines 8841-10805

# Chunk Research: sources/os/linux/linux/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of the Linux Btrfs inode implementation within `Docs/research_subset_a.md` OS/VFS and local filesystem scope. It covers VFS rename dispatch, delayed allocation flushing, symlink and tmpfile creation, preallocated extent insertion, permission checks, encoded read/write handling, swapfile activation/deactivation, inode byte accounting and assertions, in-memory inode lookup, and final VFS operation tables.

## APIs and Entry Points

- `btrfs_rename2()` validates VFS rename flags, dispatches to `btrfs_rename_exchange()` or `btrfs_rename()`, and balances dirty btrees before returning (8841-8860).
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` expose delayed-allocation flushing for snapshot creation and broader root-level writeback/reclaim (8977-9027).
- `btrfs_symlink()` creates symlinks as uncompressed inline file extents stored under a `BTRFS_EXTENT_DATA_KEY` at offset zero (9029-9132).
- `btrfs_prealloc_file_range()` and `btrfs_prealloc_file_range_trans()` wrap `__btrfs_prealloc_file_range()` for callers with or without an existing transaction (9211-9374).
- `btrfs_permission()` blocks writes to read-only roots or Btrfs read-only inodes before delegating to `generic_permission()` (9381-9395).
- `btrfs_tmpfile()` creates unnamed orphan-backed temporary files through the Btrfs new-inode path and VFS `d_tmpfile()` (9397-9456).
- Encoded I/O helpers include `btrfs_encoded_io_compression_from_extent()`, `btrfs_encoded_read_inline()`, `btrfs_encoded_read_regular_fill_pages()`, `btrfs_encoded_read_regular()`, `btrfs_encoded_read()`, and `btrfs_do_encoded_write()` (9458-10156).
- `btrfs_swap_activate()` and `btrfs_swap_deactivate()` are address-space swap hooks under `CONFIG_SWAP`; the fallback activation path returns `-EOPNOTSUPP` (10158-10621).
- `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()` provide shared inode accounting, debug validation, and xarray inode lookup helpers (10623-10709).
- The chunk ends by wiring Btrfs inode/file/address-space/dentry operations into VFS operation tables (10711-10805).

## Control Flow

`btrfs_rename2()` is a narrow adapter: unsupported flags return `-EINVAL`; `RENAME_EXCHANGE` uses the exchange-specific helper; all other supported cases use the regular rename helper with the mount idmap. The function always calls `btrfs_btree_balance_dirty()` on the destination root after the rename helper returns.

Delayed allocation flushing is centered on `start_delalloc_inodes()`. It serializes with `root->delalloc_mutex`, splices `root->delalloc_inodes` to a local list, moves each inode back to the root list before acting on it, grabs a temporary inode reference, and either queues asynchronous flush work or performs a bounded `filemap_flush_nr()`. Snapshot callers set `BTRFS_INODE_SNAPSHOT_FLUSH`; reclaim callers skip inodes marked `BTRFS_INODE_NO_DELALLOC_FLUSH`. On exit it waits for queued work completions and splices any unprocessed inodes back.

`btrfs_start_delalloc_roots()` repeats that inode-level walk across `fs_info->delalloc_roots`. It splices the root list, grabs each root with `btrfs_grab_root()`, releases the root-list spinlock while flushing, then drops the root reference. It stops on errors or exhausted write budget and restores unprocessed roots to the global list.

`btrfs_symlink()` allocates a new inode, initializes symlink mode and Btrfs address-space operations, prepares new-inode reservations, starts a transaction, creates the inode, then inserts an inline extent item containing exactly `strlen(symname)` bytes. Allocation or insertion failure after transaction start aborts the transaction and discards the new inode.

Preallocation is split between `insert_prealloc_file_extent()` and `__btrfs_prealloc_file_range()`. The insert helper builds a stack `BTRFS_FILE_EXTENT_PREALLOC` item, releases qgroup data for the target file range, and inserts through either the caller transaction or `btrfs_replace_file_extents()`. The range helper reserves disk extents in up-to-256 MiB iterations, inserts prealloc extent records, decrements block-group reservations only after the extent record exists, installs extent maps when possible, updates allocation hints and inode timestamps/version, marks `BTRFS_INODE_PREALLOC`, optionally extends `i_size`, and updates the inode item.

Encoded reads first take the inode shared lock, clamp to EOF, lock a max compressed extent-sized range, wait for or reject conflicting ordered/writeback state, and inspect an extent map. Inline extents are copied from the btree leaf into a temporary buffer and unlock before copying to the iterator. Holes and prealloc extents are returned as zeroes. Real disk extents return `-EIOCBQUEUED` while intentionally leaving inode and extent locks held for the caller to complete the disk read path with `btrfs_encoded_read_regular()`.

`btrfs_do_encoded_write()` validates compression type, encryption, checksum eligibility, compressed/unencoded size relationships, sector alignment, and i_size rules. It stages compressed data into a compressed bio, waits for ordered extents, invalidates page cache, locks the target range, reserves data/qgroup/metadata space, tries an inline compressed extent if possible, otherwise reserves a disk extent, creates an I/O extent map and ordered extent, updates i_size if needed, unlocks, releases delalloc reservations, and submits the compressed write.

Swap activation is a multi-stage validation and pinning path. It takes the inode mmap lock, waits for ordered extents, rejects incompatible inode flags, starts a filesystem exclusive operation, takes the root snapshot lock, increments `root->nr_swapfiles` after checking the root is not dead, locks the file extent range, walks file extent items, rejects holes/inline/compressed/shared extents, maps logical to physical addresses, requires single-profile one-device mappings, pins the device and block groups in `fs_info->swapfile_pins`, coalesces contiguous physical regions into swap extents, and unwinds all pins/counters on failure.

## State and Synchronization

- Delalloc flushing coordinates `root->delalloc_inodes`, `fs_info->delalloc_roots`, per-root/per-fs mutexes, spinlocks, inode references, completions, and the `flush_workers` workqueue.
- Symlink and tmpfile creation depend on `btrfs_new_inode_args` reservation state, VFS new-inode lifecycle, Btrfs transactions, and dirty btree balancing.
- Preallocation mutates qgroup reservations, data-space reservations, block-group reservation counts, file extent items, extent maps, inode ctime/version, `BTRFS_INODE_PREALLOC`, `i_size`, and disk-i-size tracking.
- Encoded I/O crosses inode locks, extent I/O tree locks, ordered extents, page cache invalidation/writeback, compressed bios, io_uring completion state, qgroup accounting, and delalloc metadata/data reservations.
- Swap activation uses `i_mmap_lock`, extent locks, `BTRFS_EXCLOP_SWAP_ACTIVATE`, `root->snapshot_lock`, `root->root_item_lock`, atomic `root->nr_swapfiles`, `fs_info->swapfile_pins_lock`, rb-tree pin records, block-group swap extent counters, chunk maps, device references, and backref share-check context.

## Dependencies

This chunk depends on Linux VFS, page-cache, bio, swap, xarray, rbtree, refcount, completion, lock, and iterator APIs. Btrfs-local dependencies include rename helpers, transaction handling, inode creation/reservation helpers, delayed allocation lists, qgroup reservation/freeing, extent allocation and freeing, extent maps, ordered extents, compressed read/write helpers, inline COW helpers, file extent replacement, extent I/O tree locking, btree path/item accessors, block-group reservation and swap counters, chunk mapping, backref sharedness checks, filesystem exclusive operations, snapshot locks, dirty btree balancing, ACL/xattr/fileattr helpers, directory operations, and dentry deletion policy.

## Risks and Edge Cases

- Delalloc flushing is intentionally whole-list and slow, and reclaim-context callers may skip inodes marked unsafe to flush.
- Workqueue delalloc flushing performs a second `filemap_flush()` when `BTRFS_INODE_HAS_ASYNC_EXTENT` is set, so callers must account for asynchronous compressed extent creation.
- Symlink targets must fit both `BTRFS_MAX_INLINE_DATA_SIZE()` and one sector; the stored inline data is not NUL-terminated.
- Preallocation has strict reservation ordering: block-group reservations are decremented only after extent insertion to avoid relocation races, and released qgroup reservations must be explicitly freed on early failure.
- Size extension during preallocation must mark the file extent range before safe disk-i-size update, or older keep-size prealloc gaps could make persisted size smaller than VFS `i_size`.
- Encoded reads use `-EIOCBQUEUED` as a lock ownership signal for disk extents; callers must not treat it like a fully unwound error path.
- Encoded writes reject NODATASUM files, unsupported encryption, malformed compression IDs, wrong LZO sector-size variants, unaligned offsets, oversized extents, zero-length input, and compressed payloads that are not smaller than the unencoded data.
- Swapfile activation rejects holes, inline extents, compressed extents, shared extents, multi-profile or multi-device mappings, read-only/scrub-blocked block groups, root deletion, concurrent snapshot creation, and concurrent exclusive operations.
- `btrfs_swap_activate()` releases the btree path before `btrfs_is_data_extent_shared()` to avoid deadlocks with transaction joins and delayed item flushing.
- `btrfs_aops` deliberately omits `.bmap`; exposing unstable Btrfs logical mappings to generic swapfile users would risk corruption.

## Cross-Chunk References

- `btrfs_rename2()` calls `btrfs_rename_exchange()` and `btrfs_rename()`, which are defined earlier in `inode.c`.
- Delalloc list insertion/removal, runtime flags, delayed iput, and writeback mechanics are established in earlier inode/writeback code.
- `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, and `btrfs_new_inode_args_destroy()` are earlier helpers that determine symlink/tmpfile reservation counts, orphan setup, and cleanup.
- Preallocation depends on earlier or external helpers such as `insert_reserved_file_extent()`, `btrfs_replace_file_extents()`, `btrfs_inode_set_file_extent_range()`, extent-map replacement, qgroup APIs, and inode update logic.
- Encoded I/O is exposed through ioctl/file code outside this chunk; this range provides the inode-side mechanics and lower-level read/write helpers.
- Swap activation ties into snapshot creation, relocation, balance, device removal/replace/resize, scrub, chunk mapping, and block-group code outside this file through exclusive operations and swapfile pins.
- The final operation tables reference many earlier functions in this file, while plugging this chunk's `btrfs_rename2()`, `btrfs_symlink()`, `btrfs_permission()`, `btrfs_tmpfile()`, `btrfs_swap_activate()`, and `btrfs_swap_deactivate()` into VFS dispatch.
