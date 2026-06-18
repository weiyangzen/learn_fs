# File Research: sources/local-fs/kdave-linux/fs/btrfs/inode.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8840, source bytes 262079, report `Docs/researches/chunks/chunk_sources_local_fs_kdave_linux_fs_btrfs_inode_c_1_1_8840_bde2cc1717a7_research.md`
- chunk 2: lines 8841-10805, source bytes 56053, report `Docs/researches/chunks/chunk_sources_local_fs_kdave_linux_fs_btrfs_inode_c_2_8841_10805_a31ddc542c3e_research.md`

## Chunk Research

### Chunk 1: lines 1-8840

# Chunk Research: sources/local-fs/kdave-linux/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/local-fs/kdave-linux/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans Btrfs inode initialization, buffered writeback/delalloc, ordered extent completion, checksum validation, orphan and delayed-iput handling, VFS inode/directory operations, extent lookup, truncation, eviction, inode creation/link/unlink, subvolume deletion, getattr, and most rename logic. It stops immediately before `btrfs_rename2()` at line 8841.

The corresponding `sources/local-fs/btrfs-linux/fs/btrfs/inode.c` file is byte-identical in this checkout; the kdave-linux line range was still treated as the authoritative chunk for this report.

## Public And Internal APIs Covered

- Locking wrappers: `btrfs_inode_lock()` / `btrfs_inode_unlock()` combine VFS inode locking with optional shared, trylock, and mmap write locking.
- Delalloc/writeback entry points: `btrfs_run_delalloc_range()`, `btrfs_set_extent_delalloc()`, `btrfs_split_delalloc_extent()`, `btrfs_merge_delalloc_extent()`, `btrfs_writepage_cow_fixup()`, `btrfs_finish_ordered_io()`, and `btrfs_finish_one_ordered()`.
- Extent APIs: `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, `btrfs_truncate_block()`, and `btrfs_cont_expand()`.
- Checksum APIs: `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()`.
- Inode lifecycle APIs: `btrfs_iget()`, `btrfs_iget_path()`, `btrfs_alloc_inode()`, `btrfs_free_inode()`, `btrfs_destroy_inode()`, `btrfs_drop_inode()`, `btrfs_init_cachep()`, `btrfs_destroy_cachep()`, `btrfs_evict_inode()`.
- Namespace operations: `btrfs_lookup_dentry()`, `btrfs_lookup()`, `btrfs_unlink_inode()`, `btrfs_unlink()`, `btrfs_rmdir()`, `btrfs_create_new_inode()`, `btrfs_add_link()`, `btrfs_create()`, `btrfs_mknod()`, `btrfs_mkdir()`, `btrfs_link()`, `btrfs_delete_subvolume()`, `btrfs_rename_exchange()`, and `btrfs_rename()`.
- Attribute and metadata APIs: `btrfs_setattr()`, `btrfs_getattr()`, `btrfs_update_inode()`, `btrfs_update_inode_fallback()`, `btrfs_update_time()`, `btrfs_orphan_add()`, and orphan cleanup helpers.

## Control Flow And Behavior

- Read/checksum error reporting starts with generic data checksum diagnostics, with special data-relocation handling that resolves logical addresses through backrefs and prints affected roots, inodes, offsets, links, paths, or metadata tree refs.
- Buffered writeback begins at `btrfs_run_delalloc_range()`. It first attempts inline extent creation for small offset-zero ranges, then chooses NOCOW/prealloc if inode flags allow, async compression if compression policy/heuristics allow, and regular COW otherwise. Zoned filesystems use `run_delalloc_cow()` to allocate then immediately submit locked ranges.
- Inline COW (`run_delalloc_inline()` and `__cow_file_range_inline()`) drops existing extents, inserts an inline file extent, updates `disk_i_size`, inode bytes, qgroup reservation, and inode item state. `ret == 1` means inline was not possible and normal writeback should continue.
- Compressed writeback uses `async_cow` / `async_chunk` / `async_extent`: `compress_file_range()` compresses and records compressed or uncompressed fallback extents; ordered work later calls `submit_compressed_extents()` and `submit_one_async_extent()` to reserve disk space, create pinned IO extent maps, create ordered extents, submit bios, or fall back to uncompressed COW.
- Regular COW is split between `cow_file_range()` and `cow_one_range()`: reserve a data extent, lock the file range, create a pinned IO extent map, allocate an ordered extent, clone relocation checksums when needed, and clear/unlock delalloc state. Zoned `-EAGAIN` can mean no active zones; the first iteration waits, later iterations can return a partial done offset.
- NOCOW writeback (`run_delalloc_nocow()`) scans file extent items, checks snapshot generations, cross refs, checksums, encoding/compression, readonly block groups, and block-group NOCOW writer pins. Non-NOCOWable gaps are coalesced and flushed through `fallback_to_cow()`.
- Ordered extent completion (`btrfs_finish_one_ordered()`) is the main persistence point for writeback: it joins a transaction, handles zoned completion, inserts RAID stripe-tree extents, converts COW/prealloc/direct/encoded ordered state into file extent items or written prealloc extents, inserts pending checksums, updates inode size/bytes, handles truncation and IO errors, releases delalloc block-group bytes, frees reserved extents on failure, and removes ordered extent references.
- Directory lookup translates directory items to inode or root keys. Root keys cross subvolume boundaries via `fixup_tree_root_location()`; missing subvolume references can synthesize a dummy simple directory inode for placeholder entries.
- Directory readdir buffers entries into a page-sized private buffer to avoid `dir_emit()` faults while tree locks are held, merges delayed dir index insert/delete lists, and caps `ctx->pos` after the last visible entry to avoid returning newly-created entries during the same scan.
- Truncate and expansion have separate flows. Expansion zeroes partial old EOF blocks, inserts explicit hole extents unless `NO_HOLES`, updates extent maps, then updates `i_size` under `snapshot_lock`. Shrink waits ordered extents, updates page cache size, calls `btrfs_truncate()`, repeatedly truncates inode items with a temporary metadata reservation, handles partial final block zeroing outside the transaction, and marks full fsync when extents were dropped.
- Eviction first truncates page cache and extent state/maps, then deletes unlinked inode items in transactions with eviction-specific reservation rules. It leaves orphan items for next mount if cleanup cannot complete.
- Create/link/unlink operations are transaction-counted around inode item, inode ref/root ref, dir item/index, parent update, ACL/xattr/security, orphan item, and delayed inode work. `btrfs_create_new_inode()` reserves an xarray slot before publishing the inode into root inode cache.
- Subvolume deletion marks the destination root dead under `subvol_sem`, rejects default subvolume/send/swapfile cases, removes root refs and UUID-tree records, inserts a tree-root orphan item, frees anon bdev, invalidates dentries, and schedules dead-root cleanup.
- Rename exchange and normal rename pin log transactions for non-root entries to prevent replay windows where neither old nor new directory entry is logged. Root/subvolume renames force full log commit and are guarded by `subvol_sem`. Normal rename also supports whiteout by creating a char-device whiteout inode after the old entry is moved.

## State And Data Structures

- Per-inode state includes `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, `disk_i_size`, `dir_index`, `index_cnt`, `runtime_flags`, compression properties, root pointer, and delayed node/iput/list membership.
- Per-root and fs-wide state used here includes `root->inodes` xarray, `root->delalloc_inodes`, `root->nr_delalloc_inodes`, `fs_info->delalloc_roots`, `async_delalloc_pages`, `delayed_iputs`, `nr_delayed_iputs`, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, `data_sinfo`, block reservations, qgroup reservations, and cleaner/fixup/delalloc worker queues.
- Extent state flags drive accounting and correctness: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_FINISHING_ORDERED`, `EXTENT_NODATASUM`, and `QGROUP_RESERVED`.
- Ordered extent flags distinguish `BTRFS_ORDERED_REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`, `DIRECT`, `ENCODED`, `TRUNCATED`, and `IOERR`. The code is careful about which cleanup path owns metadata/data/qgroup reservations for each flag mix.
- Btree item state touched in this chunk includes inode items, inode refs/extrefs, dir items, dir index items, file extent items, hole extents, orphan items, root refs/backrefs, root items, UUID-tree entries, csum items, and RAID stripe-tree extent records.

## Dependencies

- VFS/MM integration: inode/dentry/file operations, folios, address-space ops, page cache, `i_rwsem`, `i_mmap_lock`, `truncate_setsize()`, `pagecache_isize_extended()`, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACL, LSM xattrs, fscrypt, and migration hooks.
- Btrfs subsystems: transactions, delayed inode/items, ordered data, extent maps, extent I/O, compression, qgroups, relocation/backrefs, root tree, dir items, file items, inode items, tree log, UUID tree, orphan items, space/block groups, zoned allocator, RAID stripe tree, verity, subpage state, and free-space inode handling.
- Cross-file callers visible by search include `extent_io.c` for `btrfs_run_delalloc_range()` and `btrfs_get_extent()`, `bio.c` for `btrfs_data_csum_ok()`, `ordered-data.c` for `btrfs_finish_ordered_io()`, `direct-io.c` and `file.c` for `can_nocow_extent()` and extent lookup, `ioctl.c` for `btrfs_create_new_inode()`, and inode tests for `btrfs_get_extent()`.

## Risks And Invariants

- Reservation ownership is the largest risk surface: data space, metadata reservations, qgroup reservations, block-group `delalloc_bytes`, inode byte counts, and ordered-extent cleanup are intentionally split across writeback, ordered completion, truncate, invalidate, and eviction.
- Error paths must not clear `EXTENT_DO_ACCOUNTING`, metadata reservations, or data reservations from the wrong owner. Several paths deliberately avoid clearing flags because ordered extent completion owns the accounting.
- Lock ordering is fragile: extent locks precede transaction joins in ordered completion; path locks are released before memory allocation or long backref walks; delayed iput locks are IRQ-safe; inode/root/subvolume locks protect xarray, delalloc lists, and subvolume deletion.
- Log replay/fsync correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning during rename, `btrfs_record_unlink_dir()`, `btrfs_log_new_name()`, and forced full commits for subvolume/root renames.
- Inline extents are tightly constrained: offset 0 only, size at most filesystem sector and page, not full sector uncompressed, not encrypted, and must cover the whole file.
- NOCOW is conservative: it rejects shared/snapshotted/csum-bearing/compressed/encoded/readonly extents and prealloc ranges with overlapping delalloc. Misclassification risks stale checksums or writes into shared extents.
- Subpage/blocksize mismatches are explicitly handled in checksum, truncate, invalidate, and release paths. Waiting on the subpage spinlock before releasing folio private state avoids use-after-free with endio.
- Orphan cleanup has special cases for dead roots, fsverity metadata, historical truncate orphan items, and reused inode numbers. Failure leaves orphan items for later mount cleanup.
- Rename and exchange have replay windows if log pinning or full-commit forcing is wrong. Whiteout creation also has a delayed cleanup path through `btrfs_new_inode_args_destroy()` and `iput()`.

## Cross-Chunk References

- The chunk ends just before `btrfs_rename2()` at line 8841. Later code wires `btrfs_rename()` / `btrfs_rename_exchange()` into VFS inode operations and balances dirty btrees after rename.
- Later same-file sections outside this chunk define delalloc root flushing, symlink creation, preallocation/fallocate helpers, permission/tmpfile handlers, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and final operation tables. This chunk calls or prepares state for several of those later APIs.
- `btrfs_update_inode_bytes()` and `btrfs_assert_inode_range_clean()` are referenced here but defined later in the file, so final per-file research should connect inode byte accounting and extent-state assertions back to the writeback/truncate paths above.
- `btrfs_file_operations` is assigned in this chunk but defined in another file; `btrfs_aops` and inode operation tables are declared here but defined after the chunk boundary.

### Chunk 2: lines 8841-10805

# Chunk Research: sources/local-fs/kdave-linux/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of Btrfs inode/VFS implementation in `sources/local-fs/kdave-linux/fs/btrfs/inode.c`, within `Docs/research_subset_a.md` local filesystem scope. It covers rename dispatch, delayed allocation flushing, symlink and tmpfile creation, file preallocation extent insertion, permission checks, encoded read/write support, swapfile activation/deactivation, inode byte accounting/assertion helpers, inode lookup by number, and the final VFS operation tables for Btrfs directory/file/special/symlink inodes, address spaces, and dentries.

## APIs and Entry Points

- `btrfs_rename2()` is the VFS `.rename` adapter. It validates `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`, dispatches to `btrfs_rename_exchange()` or `btrfs_rename()`, then balances dirty btrees.
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` flush pending delayed allocation for one root during snapshotting or across all roots for writeback/reclaim.
- `btrfs_symlink()` implements VFS symlink creation using an inline `BTRFS_EXTENT_DATA_KEY` item containing the target path.
- `btrfs_prealloc_file_range()` and `btrfs_prealloc_file_range_trans()` reserve disk extents and insert `BTRFS_FILE_EXTENT_PREALLOC` records, with or without a caller-supplied transaction.
- `btrfs_permission()` enforces read-only root and inode flags before delegating to `generic_permission()`.
- `btrfs_tmpfile()` implements unnamed temporary file creation through Btrfs new-inode/orphan machinery and `d_tmpfile()`.
- `btrfs_encoded_io_compression_from_extent()`, `btrfs_encoded_read()`, `btrfs_encoded_read_regular()`, `btrfs_encoded_read_regular_fill_pages()`, and `btrfs_do_encoded_write()` implement encoded I/O paths for compressed extents, inline extents, regular extents, prealloc extents, and holes.
- `btrfs_swap_activate()` and `btrfs_swap_deactivate()` are installed as address-space swap hooks when `CONFIG_SWAP` is enabled; otherwise activation returns `-EOPNOTSUPP`.
- `btrfs_update_inode_bytes()` atomically adjusts VFS inode block usage counters after extent replacement operations.
- `btrfs_assert_inode_range_clean()` is an assertion helper for callers that have fully flushed and locked a file range.
- `btrfs_find_first_inode()` returns a referenced in-memory inode at or after a requested inode number.
- The chunk ends by defining `btrfs_dir_inode_operations`, `btrfs_dir_file_operations`, `btrfs_aops`, `btrfs_file_inode_operations`, `btrfs_special_inode_operations`, `btrfs_symlink_inode_operations`, and `btrfs_dentry_operations`.

## Control Flow

`btrfs_rename2()` is a thin flag gate. Unsupported flags immediately return `-EINVAL`; exchange renames call the dedicated exchange path, while normal/no-replace/whiteout renames call the main rename helper. Dirty metadata balancing is performed against the destination directory root before returning.

Delayed allocation flushing is coordinated by `start_delalloc_inodes()`. It serializes with `root->delalloc_mutex`, splices `root->delalloc_inodes` into a private list, then cycles each inode back to the root list before attempting an `igrab()`. Reclaim-context callers skip inodes with `BTRFS_INODE_NO_DELALLOC_FLUSH`. Snapshot flushes set `BTRFS_INODE_SNAPSHOT_FLUSH`. Unlimited flushes allocate `btrfs_delalloc_work`, queue work on `fs_info->flush_workers`, and later wait for every completion; bounded flushes call `filemap_flush_nr()` directly and stop on error or when the write budget reaches zero. Any unprocessed spliced entries are appended back under the delalloc spinlock.

`btrfs_start_delalloc_roots()` applies that inode-level logic across `fs_info->delalloc_roots`. It splices the global root list, grabs each root, moves it back to the global list, drops the root-list spinlock while flushing inodes, then puts the root. It preserves unprocessed roots on early exit. Both public delalloc entry points refuse work on a filesystem already in error state with `-EROFS`.

`btrfs_symlink()` creates a new inode, initializes it as a symlink, sets Btrfs address-space operations, records the symlink size, prepares new-inode metadata reservations, starts a transaction, creates the inode item, then inserts one inline file extent item at offset zero. The inline extent is marked uncompressed/unencrypted, its `ram_bytes` is the symlink length, and the target bytes are copied directly into the leaf. On path allocation or insert failure after inode creation, it aborts the transaction and discards the new inode.

Preallocation is split between `insert_prealloc_file_extent()` and `__btrfs_prealloc_file_range()`. The insert helper builds an in-memory `btrfs_file_extent_item` with `BTRFS_FILE_EXTENT_PREALLOC`, releases qgroup data for the file range, then either inserts into an existing transaction through `insert_reserved_file_extent()` or calls `btrfs_replace_file_extents()` to create/extend a transaction. Early failures free the qgroup reservation that was released at function entry. The range-level helper reserves disk extents in chunks capped at 256 MiB and adjusted by `min_size` and previous allocation size, inserts each prealloc extent, decrements block-group reservations only after extent insertion, installs an extent map when possible, updates allocation hints, ctime, inode version, and `BTRFS_INODE_PREALLOC`, and optionally extends `i_size`. Before extending size, it explicitly marks the file extent range covering old-to-new size so `btrfs_inode_safe_disk_i_size_write()` cannot persist a smaller size because of a gap left by prior keep-size preallocation.

Encoded reads acquire a shared inode lock, align and lock an extent range, wait for or reject overlapping ordered extents depending on `IOCB_NOWAIT`, and inspect the extent map at the read position. Inline extents are handled by looking up the file extent item, copying inline bytes to a temporary buffer, then unlocking before copying to the iterator. Holes and prealloc extents are returned as zeroes. Compressed regular extents require the caller buffer to hold the full compressed extent and return encoded metadata such as `unencoded_len`, `unencoded_offset`, and compression type. Non-hole regular/compressed reads return `-EIOCBQUEUED` with inode and extent locks intentionally left held so the follow-on read path can submit I/O and unlock after completion.

`btrfs_encoded_read_regular_fill_pages()` allocates one or more Btrfs bios over caller-supplied pages. It tracks all submitted bios with `btrfs_encoded_read_private.pending_refs`; end I/O stores the first block status and completes either an io_uring context or a synchronous completion. `btrfs_encoded_read_regular()` allocates pages, fills them from disk, unlocks the inode/range, then copies either the full compressed byte stream or the requested uncompressed window to the iterator.

`btrfs_do_encoded_write()` validates the userspace encoded-write contract, including compression type, LZO sector-size variant, no encryption, no `NODATASUM`, size limits, compression ratio, sector-aligned start and unencoded offset, and allowed EOF unaligned logical length. It copies compressed bytes into compressed-write folios, zero-pads to sector alignment, waits for ordered extents, invalidates page cache, locks the target range, reserves data/qgroup/metadata, tries inline COW for eligible single-inline writes, otherwise reserves an extent, creates an I/O extent map and encoded compressed ordered extent, advances `i_size` when needed, unlocks, releases delalloc reservations, and submits the compressed write. Error labels unwind reserved extents, block-group reservation counts, metadata/data/qgroup reservations, extent locks, and compressed bio resources.

Swapfile activation flushes ordered extents, verifies the inode is not compressed and is `NODATACOW|NODATASUM`, allocates a btree path and backref share-check context, starts an exclusive swap-activation operation, blocks snapshot creation with `root->snapshot_lock`, rejects dead roots, increments `root->nr_swapfiles`, locks the file extent range, and walks all file extent items up to sector-aligned `i_size`. Each extent must be non-inline, uncompressed, non-hole, unshared, single-profile, and mapped to the same device. The code pins the device and each block group in `fs_info->swapfile_pins`, increments block-group swap extent counters, merges physically contiguous extents into swap extents, checks for fatal signals, and returns the number of extents after setting `sis` and `span`. Any error deactivates pins and decrements the root swapfile counter.

The final helper and operation-table section provides small glue: byte accounting under `inode->lock`, assertion-only ordered extent detection, xarray-based referenced inode lookup with rescheduling if `igrab()` fails, and VFS callback tables that bind earlier functions and this chunk's symlink/tmpfile/permission/swap hooks into the kernel.

## State and Synchronization

- Delalloc state is held in `root->delalloc_inodes` and `fs_info->delalloc_roots`, protected by paired mutexes and spinlocks. Workqueue flushes retain inodes with `igrab()` and release them in `btrfs_run_delalloc_work()`.
- Snapshot-related delalloc flushing uses `BTRFS_INODE_SNAPSHOT_FLUSH`; reclaim avoidance uses `BTRFS_INODE_NO_DELALLOC_FLUSH`; asynchronous compressed/delayed extents may force a second `filemap_flush()`.
- Symlink and tmpfile creation rely on `btrfs_new_inode_args` lifecycle, transaction item counts, VFS new-inode state, and Btrfs inline extent item state.
- Preallocation updates qgroup reservations, data-space reservations, block-group reservations, extent maps, inode size/disk size, ctime, inode version, and `BTRFS_INODE_PREALLOC`.
- Encoded I/O coordinates inode locks, extent locks, ordered extents, page cache invalidation/writeback, compressed bios, qgroup/delalloc accounting, extent maps, and `ki_pos` advancement.
- Swapfile activation uses `i_mmap_lock`, extent I/O tree locks, `btrfs_exclop_start()/finish()`, `root->snapshot_lock`, `root->root_item_lock`, atomic `root->nr_swapfiles`, `fs_info->swapfile_pins_lock`, rb-tree pin storage, block-group swap extent counters, device references, and backref share checks.
- `btrfs_find_first_inode()` reads `root->inodes` under the xarray lock, then takes a live VFS inode reference with `igrab()` before returning.

## Dependencies

This chunk depends on VFS APIs, Linux concurrency primitives, and Btrfs subsystems from earlier code and other files.

Important Btrfs-local dependencies include transaction helpers, new-inode helpers, delayed allocation lists, qgroup accounting, extent allocation/freeing, block-group reservation and swap counters, extent maps, ordered extents, compressed write/read bio helpers, inline COW helpers, extent I/O tree locking, root snapshot/exclusive-operation locking, chunk mapping, backref sharedness checks, scrub state, inode item updates, file-extent tree tracking, dirty btree balancing, io_uring encoded-read completion, ACL/xattr/fileattr helpers, directory iteration/open/release/sync helpers, and dentry deletion policy.

Specific cross-file dependencies visible from the calls include `btrfs_replace_file_extents()` in `fs/btrfs/file.c`, `btrfs_alloc_ordered_extent()` in `fs/btrfs/ordered-data.c`, and `btrfs_submit_compressed_write()` in `fs/btrfs/compression.c`. The operation tables also depend on numerous inode, directory, ioctl, ACL, xattr, fileattr, read/write, and page-cache helpers defined earlier in this file or neighboring Btrfs modules.

## Risks and Edge Cases

- `start_delalloc_inodes()` has intentionally slow whole-list behavior and can skip reclaim-sensitive inodes, so callers must tolerate partial flushing in reclaim contexts.
- Symlink targets must fit both Btrfs inline limits and the filesystem sector size. No NUL byte is stored as part of the inline extent; the length is exactly `strlen(symname)`.
- Preallocation relies on careful reservation ordering: block-group reservations are decremented after file extent insertion to avoid relocation races, and qgroup release must be freed manually on early errors.
- The preallocation size-extension path explicitly repairs file-extent range tracking before calling `btrfs_inode_safe_disk_i_size_write()`, highlighting a persistence risk from previous keep-size prealloc extents that outlived mount-time extent-map population.
- Encoded read leaves inode and extent locks held when it returns `-EIOCBQUEUED` for non-hole disk reads. Correct callers must finish through the regular read path and unlock there.
- Encoded writes reject uncompressed/no-compression encoded data, encrypted data, `NODATASUM` files, badly aligned offsets, overly large extents, and compressed data that is not smaller than unencoded data.
- Encoded write has multiple reservation domains with separate unwind paths; wrong error-label ordering would leak qgroup/data/metadata reservations or free an extent after ownership has moved to an ordered extent.
- Swapfile activation rejects holes, inline extents, compressed extents, shared data extents, multi-device/profile mappings, extents crossing devices, and read-only/scrub-pinned block groups.
- `btrfs_swap_activate()` must release the btree path before `btrfs_is_data_extent_shared()` to avoid deadlocks with transaction joins and delayed item flushing.
- The address-space operations deliberately omit `.bmap`; exposing mutable Btrfs logical mappings to generic swapfile bmap users would risk corruption.
- `btrfs_add_swapfile_pin()` returns `1` for already-pinned entries and increments block-group extent counts only for block-group pins, so callers must normalize `1` to success without skipping matching reference ownership.

## Cross-Chunk References

- `btrfs_rename2()` depends on `btrfs_rename_exchange()` and `btrfs_rename()` defined before this chunk.
- Delalloc list membership, inode runtime flags, root/fs-info delalloc list management, and delayed iput behavior are established earlier in this file and surrounding Btrfs writeback code.
- `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, and `btrfs_new_inode_args_destroy()` are defined earlier and govern symlink/tmpfile transaction reservations and orphan behavior.
- Preallocation calls `insert_reserved_file_extent()`, `btrfs_replace_file_extents()`, extent-map replacement, qgroup helpers, and inode file-extent range tracking implemented outside this chunk or earlier in the file.
- Encoded read/write entry points are likely called from ioctl or file-operation code outside this line range; this chunk implements the inode-side mechanics but not the userspace ioctl dispatcher.
- Swapfile activation ties into snapshot creation, relocation, balance, device replace/remove/resize, scrub, and block-group code outside this file through exclusive operations, snapshot locks, swapfile pin checks, and block-group swap counters.
- The operation tables at the end reference many functions defined in earlier chunks of `inode.c` and connect this chunk's local implementations into the kernel VFS.
