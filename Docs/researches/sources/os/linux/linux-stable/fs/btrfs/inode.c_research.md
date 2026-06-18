# File Research: sources/os/linux/linux-stable/fs/btrfs/inode.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8840, source bytes 262079, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_btrfs_inode_c_1_1_8840_d3366440c5ce_research.md`
- chunk 2: lines 8841-10805, source bytes 56053, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_btrfs_inode_c_2_8841_10805_2644b90a541a_research.md`

## Chunk Research

### Chunk 1: lines 1-8840

# Chunk Research: sources/os/linux/linux-stable/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/os/linux/linux-stable/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans the start of Btrfs inode support through checksum diagnostics, inode locking, buffered writeback and delayed allocation, COW/NOCOW/compressed extent setup, ordered extent completion, delayed iput and orphan cleanup, inode load/update, unlink/rmdir/subvolume deletion, truncation and expansion, eviction, lookup/readdir, inode creation/link/mkdir/mknod, extent lookup, NOCOW checks, folio invalidation/release, inode cache lifecycle, getattr, rename exchange, and most of normal rename. The chunk stops immediately before `btrfs_rename2()` at line 8841.

## Public And Internal APIs Covered

- Locking/state helpers: `btrfs_inode_lock()`, `btrfs_inode_unlock()`, delalloc extent set/clear/split/merge helpers.
- Writeback/delalloc APIs: `btrfs_run_delalloc_range()`, `btrfs_writepage_cow_fixup()`, ordered extent finish helpers, inline/compressed/COW/NOCOW paths.
- Extent/checksum APIs: `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, truncate/expand helpers, block checksum calculation/validation.
- Inode lifecycle APIs: `btrfs_iget*()`, alloc/free/destroy/drop inode, cache init/destroy, eviction.
- Namespace/VFS ops: lookup, opendir/readdir, dirty/update-time, create, mknod, mkdir, link, unlink, rmdir, subvolume deletion, rename exchange, and normal rename.

## Control Flow And Behavior

- `btrfs_run_delalloc_range()` dispatches buffered writeback: inline extent attempt, NOCOW/prealloc, async compression, then regular COW. Zoned filesystems use allocation plus immediate locked-range submission.
- Inline writeback is limited to offset-zero, one-folio/page, sector-sized-or-smaller, whole-file, unencrypted data, and falls back on metadata ENOSPC.
- Compression records `async_extent` work, rejects poor compression ratios unless forced/property-driven, then submits compressed ordered extents or falls back to uncompressed COW.
- NOCOW is conservative: it rejects shared/snapshotted, csum-bearing, compressed/encrypted/encoded, explicit-hole, readonly, or unsafe prealloc ranges, then COWs unsafe gaps.
- Ordered extent completion persists writeback into the btree: handles IO errors, truncation, zoned completion, RAID stripe-tree records, file extent insertion/prealloc conversion, checksum insertion, inode byte/size updates, and reservation cleanup.
- Orphan cleanup scans orphan items, skips dead roots, cleans incomplete fsverity metadata, deletes obsolete truncate-orphan entries, and relies on eviction via `iput()` for unlinked inodes.
- Inode loading fills VFS/Btrfs state, sets pessimistic fsync replay markers after reload, initializes extent tracking, assigns operation tables, and publishes into `root->inodes`.
- Truncate/expand zero partial blocks, insert holes unless `NO_HOLES`, manipulate extent maps, wait ordered extents, and force full fsync when extents are dropped.
- Rename/exchange count transaction items, handle root refs vs inode refs, pin tree logs for non-root renames, force full commits for subvolume/root entries, and support whiteout creation.

## State And Data Structures

- Per-inode: `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, delalloc/new/defrag/csum byte counters, `disk_i_size`, `dir_index`, `index_cnt`, runtime flags, compression policy, delayed iput/node state, root pointer, and log transaction fields.
- Per-root/fs: inode xarray, delalloc inode/root lists, async delalloc counters, delayed iputs, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, block reservations, qgroup reservations, and worker queues.
- Extent flags: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, reservation-clear flags, `EXTENT_FINISHING_ORDERED`, and `EXTENT_NODATASUM`.
- Ordered extent flags distinguish regular, NOCOW, prealloc, compressed, direct, encoded, truncated, and IO-error states.

## Dependencies

- VFS/MM: inode/dentry/file ops, folios, page cache, locks, truncate helpers, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACLs, fscrypt, LSM xattrs, fsverity, migration, and whiteout support.
- Btrfs subsystems: transactions, delayed items, ordered data, extent maps/I/O trees, compression, qgroups, relocation/backrefs, root/dir/file/inode items, tree log, UUID tree, orphan items, block groups, zoned allocator, RAID stripe tree, verity, subpage state, and properties.
- Cross-file users include extent I/O writeback, bio checksum validation, ordered-data completion, direct/file/encoded write paths, and ioctl/subvolume creation paths.

## Risks And Invariants

- Reservation ownership is the main risk: metadata, data-space, qgroup, delalloc block-group bytes, inode bytes, and ordered extent refs are split across phases.
- Error paths must clear only owned flags; some paths intentionally leave accounting for ordered completion.
- Lock ordering is fragile around extent locks, transaction joins, btree paths, delayed iput IRQ locking, `subvol_sem`, folio writeback, and subpage spinlocks.
- Fsync/log replay correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning, unlink records, and forced full commits for root entries.
- Stable-specific note: this linux-stable chunk uses `icount_read(&inode->vfs_inode)` in `btrfs_prune_dentries()`, while the sibling mainline chunk uses `icount_read_once()`.

## Cross-Chunk References

- This chunk ends before `btrfs_rename2()` at line 8841.
- Later same-file code defines delalloc root flushing, symlink creation, preallocation/fallocate, permission/tmpfile handlers, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and operation tables.
- `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()` are referenced here but defined later.
- `btrfs_file_operations` is assigned here but defined elsewhere; `btrfs_aops` and inode operation tables are declared here and defined after the chunk boundary.

### Chunk 2: lines 8841-10805

# Chunk Research: sources/os/linux/linux-stable/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of Linux-stable Btrfs `inode.c` in `Docs/research_subset_a.md` scope. It covers the VFS rename adapter, delayed allocation flushing across inode/root lists, symlink and tmpfile inode creation, preallocated file extent insertion, permission checks, encoded read/write helpers for compressed extents, swapfile activation/deactivation, inode byte and range-clean assertions, inode lookup by number, and final Btrfs operation tables for directory, file, special, symlink, address-space, and dentry behavior.

## APIs and Entry Points

- `btrfs_rename2()` is the VFS `.rename` entry point. It accepts `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`, dispatches to earlier `btrfs_rename_exchange()` or `btrfs_rename()`, then triggers dirty btree balancing.
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` expose delayed-allocation flushing to snapshot, qgroup, reclaim, ioctl, device-replace, and transaction paths.
- `btrfs_symlink()` creates symlink inodes backed by uncompressed inline extent data.
- `btrfs_prealloc_file_range()` and `btrfs_prealloc_file_range_trans()` wrap `__btrfs_prealloc_file_range()` to reserve disk extents and insert `BTRFS_FILE_EXTENT_PREALLOC` records with or without an existing transaction.
- `btrfs_permission()` enforces readonly-root and readonly-inode write denial before `generic_permission()`.
- `btrfs_tmpfile()` implements unnamed temporary file creation through orphan-backed new-inode setup and `d_tmpfile()`.
- Encoded I/O APIs include `btrfs_encoded_read()`, `btrfs_encoded_read_regular()`, `btrfs_encoded_read_regular_fill_pages()`, and `btrfs_do_encoded_write()`.
- Under `CONFIG_SWAP`, `.swap_activate` and `.swap_deactivate` are implemented by `btrfs_swap_activate()` and `btrfs_swap_deactivate()`; otherwise activation returns `-EOPNOTSUPP`.

## Control Flow

Delayed-allocation flushing serializes on root/filesystem delalloc mutexes, splices pending lists, grabs inode/root references, queues async flush work for unbounded flushes, or calls `filemap_flush_nr()` for bounded flushes. Reclaim callers may skip inodes flagged `BTRFS_INODE_NO_DELALLOC_FLUSH`.

Symlink creation allocates and initializes an inode, reserves new-inode metadata, starts a transaction, creates the inode, inserts a `BTRFS_EXTENT_DATA_KEY`, fills a `BTRFS_FILE_EXTENT_INLINE` item, instantiates the dentry, ends the transaction, and balances dirty btrees.

Preallocation reserves extents in chunks, inserts prealloc file extents, updates extent maps, decrements block-group reservations only after file extent insertion, and safely advances `i_size`/disk-i-size after marking the full old-to-new file-extent range.

Encoded read locks the inode and extent range, rejects or waits for ordered extents, resolves extent maps, handles inline data, holes/prealloc zeroing, compressed extents, and leaves locks held with `-EIOCBQUEUED` when the caller must submit disk I/O.

Encoded write validates compression/alignment/size constraints, copies compressed user data into compressed-write folios, waits and invalidates overlapping cache, reserves data/qgroup/metadata, tries inline COW, otherwise reserves disk space, creates an I/O extent map and encoded compressed ordered extent, updates `i_size`, and submits compressed write I/O.

Swap activation waits for ordered extents, rejects compressed/COW/checksummed files, blocks relocation/balance/device/snapshot races, rejects dead roots, locks the file range, verifies every extent is explicit, non-inline, uncompressed, unshared, single-profile, and on one device, then pins devices/block groups and registers physical swap extents.

## State and Dependencies

State touched includes delalloc inode/root lists, inode runtime flags, qgroup/data/metadata reservations, block-group reservation and swap counters, extent maps, file extent items, ordered extents, compressed bios, pagecache state, extent I/O locks, swapfile pin rb-trees, root swapfile counters, exclusive-operation state, snapshot locks, VFS inode bytes, and root inode xarrays.

In-file dependencies defined earlier include `btrfs_rename_exchange()`, `btrfs_rename()`, `insert_reserved_file_extent()`, `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, inline COW helpers, extent-map creation, and many callbacks used by the final operation tables.

Cross-file dependencies include `btrfs_replace_file_extents()` in `file.c`, `btrfs_alloc_ordered_extent()` in `ordered-data.c`, compressed-bio helpers in `compression.c/.h`, encoded ioctl/io_uring frontends in `ioctl.c`, share detection in `backref.c`, chunk mapping and swapfile-pin checks in `volumes.c`, and exclusive-operation helpers in `fs.c`.

## Risks and Cross-Chunk References

- Delalloc flushing depends on correct list restoration, reference handling, and async completion before freeing work items.
- Preallocation has fragile reservation and size-persistence ordering, especially around keep-size gaps and safe disk-i-size updates.
- Encoded read transfers lock ownership across `-EIOCBQUEUED`; callers must unlock exactly once.
- Encoded write tracks different logical, unencoded, and compressed disk byte counts, making unwind ordering error-prone.
- Swap activation must reject holes, inline extents, compression, shared/COW extents, multi-device/profile mappings, readonly/scrub-affected block groups, dead roots, and snapshot races to avoid direct swap I/O corruption.
- Earlier chunks of this same file define rename, new-inode, extent insertion, inline COW, read/write address-space callbacks, and other operation-table targets.
- `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()` are used by file extent replacement, reflink, tree-log, inode extent updates, and relocation code.
