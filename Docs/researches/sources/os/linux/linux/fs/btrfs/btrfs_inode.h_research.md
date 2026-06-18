# File Research: sources/os/linux/linux/fs/btrfs/btrfs_inode.h

## Scope And Role

`btrfs_inode.h` defines Btrfs' in-memory inode wrapper, inode runtime flags, inode helper functions, and prototypes for inode operations implemented across Btrfs. It is the main interface between VFS inodes and Btrfs-specific metadata, extent mapping, delayed allocation, fsync/logging, orphan handling, encoded I/O, checksums, and inode lifecycle management.

The central type is `struct btrfs_inode`, which embeds `struct inode vfs_inode` as the VFS-facing object and adds Btrfs state.

## Constants And Runtime Flags

`BTRFS_DIR_START_INDEX` is `2`, because directory positions `0` and `1` are reserved for `.` and `..`.

The runtime flag enum includes flags for:

- Close/writeback behavior: `BTRFS_INODE_FLUSH_ON_CLOSE`.
- Dummy/free-space/root-stub special inodes.
- Defrag and async extents.
- Full fsync/logging behavior.
- Property/xattr/capability cache state.
- Snapshot flush.
- Delalloc deadlock avoidance: `BTRFS_INODE_NO_DELALLOC_FLUSH`.
- Verity setup serialization.
- COW write error tracking.

Several comments document strict locking requirements:
- `BTRFS_INODE_NEEDS_FULL_SYNC` must be set under the VFS inode lock except during safe initialization/loading contexts.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` avoids deadlock when dirty pages in a locked range need a transaction reservation.
- `BTRFS_INODE_ROOT_STUB` represents a subvolume dentry without a root reference in snapshot/subvolume nesting cases.

## Main Structure

`struct btrfs_inode` includes:

- Root and inode identity:
  - `root`
  - `objectid` on 32-bit systems
  - `generation`
  - `vfs_inode`

- Compression/defrag properties:
  - `prop_compress`
  - `defrag_compress`
  - `defrag_compress_level`

- Core locks and mapping trees:
  - `lock`
  - `extent_tree`
  - `io_tree`
  - optional `file_extent_tree`
  - `log_mutex`
  - `ordered_tree_lock`
  - `i_mmap_lock`

- Delalloc and extent accounting:
  - `outstanding_extents`
  - ordered extent rb tree and cache pointer
  - `delalloc_inodes` list
  - `delalloc_bytes`
  - `new_delalloc_bytes`
  - `defrag_bytes`
  - `disk_i_size`
  - `csum_bytes`

- Fsync/logging fields:
  - `last_trans`
  - `logged_trans`
  - `last_sub_trans`
  - `last_log_commit`
  - directory log index state
  - `last_unlink_trans`
  - `last_reflink_trans`

- Directory and subvolume state:
  - `index_cnt`
  - `dir_index`
  - `first_dir_index_to_log`
  - `last_dir_index_offset`
  - `ref_root_id` for root stubs

- On-disk inode flags:
  - `flags`
  - `ro_flags`

- Reservation and delayed work:
  - embedded `struct btrfs_block_rsv block_rsv`
  - `delayed_node`
  - `delayed_iput`

- Creation time:
  - `i_otime_sec`
  - `i_otime_nsec`

Many fields are protected by `lock`, `log_mutex`, the VFS inode lock, or are specific to directories/files/data relocation as documented inline.

## Important Helpers

Directory log index helpers:
- `btrfs_get_first_dir_index_to_log()`
- `btrfs_set_first_dir_index_to_log()`

`BTRFS_I()` is a type-checked and const-preserving macro that converts a VFS `struct inode *` to `struct btrfs_inode *`.

`btrfs_inode_hash()` hashes inode objectid and root objectid, folding to 32 bits on 32-bit systems.

`btrfs_ino()` returns the Btrfs inode number. On 32-bit systems it uses the stored 64-bit `objectid`, except root stubs use `vfs_inode.i_ino`.

`btrfs_get_inode_key()` fills a `BTRFS_INODE_ITEM_KEY`.

`btrfs_set_inode_number()` updates both Btrfs and VFS inode numbers as needed.

`btrfs_i_size_write()` writes VFS inode size and Btrfs `disk_i_size`.

`btrfs_is_free_space_inode()` checks the free-space-inode runtime flag.

`is_data_inode()` excludes the btree inode objectid.

`btrfs_mod_outstanding_extents()` adjusts outstanding extent count and emits a tracepoint except for free-space inodes.

`btrfs_set_inode_last_sub_trans()` records log transaction modification after buffered, direct, or mmap writes.

`btrfs_set_inode_full_sync()` marks full fsync needed and pessimistically advances `last_reflink_trans` to at least `last_trans`.

`btrfs_inode_in_log()` checks whether the inode is already logged for a generation.

`btrfs_inode_can_compress()` rejects compression for `NODATACOW` or `NODATASUM`.

`btrfs_assert_inode_locked()` asserts VFS inode lock ownership.

`btrfs_update_inode_mapping_flags()` maps `NODATASUM` to stable-writes behavior.

`btrfs_set_inode_mapping_order()` sets folio order ranges under experimental config for data inodes.

## Declared API Groups

Checksum and data integrity:
- `btrfs_calculate_block_csum_folio()`
- `btrfs_calculate_block_csum_pages()`
- `btrfs_check_block_csum()`
- `btrfs_data_csum_ok()`

NOCOW and extents:
- `can_nocow_extent()`
- `btrfs_get_extent()`
- `btrfs_get_extent_allocation_hint()`
- `btrfs_create_io_em()`

Directory/link/subvolume:
- `btrfs_lookup_dentry()`
- `btrfs_set_inode_index()`
- `btrfs_unlink_inode()`
- `btrfs_add_link()`
- `btrfs_delete_subvolume()`

Truncation/expansion/preallocation:
- `btrfs_truncate_block()`
- `btrfs_cont_expand()`
- `btrfs_prealloc_file_range()`
- `btrfs_prealloc_file_range_trans()`

Delalloc:
- `btrfs_del_delalloc_inode()`
- `btrfs_start_delalloc_snapshot()`
- `btrfs_start_delalloc_roots()`
- `btrfs_set_extent_delalloc()`
- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`
- `btrfs_split_delalloc_extent()`
- `btrfs_run_delalloc_range()`
- `btrfs_writepage_cow_fixup()`

New inode creation:
- `struct btrfs_new_inode_args`
- `btrfs_new_inode_prepare()`
- `btrfs_create_new_inode()`
- `btrfs_new_inode_args_destroy()`
- `btrfs_new_subvol_inode()`

Lifecycle/cache:
- `btrfs_evict_inode()`
- `btrfs_alloc_inode()`
- `btrfs_destroy_inode()`
- `btrfs_free_inode()`
- `btrfs_drop_inode()`
- `btrfs_init_cachep()`
- `btrfs_destroy_cachep()`
- `btrfs_iget_path()`
- `btrfs_iget()`

Metadata/orphan/delayed iput:
- `btrfs_update_inode()`
- `btrfs_update_inode_fallback()`
- `btrfs_orphan_add()`
- `btrfs_orphan_cleanup()`
- `btrfs_add_delayed_iput()`
- `btrfs_run_delayed_iputs()`
- `btrfs_wait_on_delayed_iputs()`

Encoded I/O:
- `btrfs_encoded_io_compression_from_extent()`
- `btrfs_encoded_read_regular_fill_pages()`
- `btrfs_encoded_read()`
- `btrfs_encoded_read_regular()`
- `btrfs_do_encoded_write()`

Locking and bytes:
- `btrfs_inode_lock()`
- `btrfs_inode_unlock()`
- `btrfs_update_inode_bytes()`
- `btrfs_assert_inode_range_clean()`

## Integration Points

This header includes VFS, mm, fscrypt, tracepoints, Btrfs ctree definitions, block reserves, extent maps, and extent I/O trees.

It connects inode code with:
- Delalloc and ordered extents.
- Extent maps and file extent items.
- Checksums and bio validation.
- Tree logging/fsync.
- Subvolume lookup/deletion.
- Orphan cleanup.
- Encoded read/write ioctls.
- Compression, verity, fscrypt, and qgroup-related accounting through downstream implementations.

## Concurrency Notes

`struct btrfs_inode::lock` protects most inode accounting and fsync fields.

`log_mutex` protects inode logging and directory log offset state.

`ordered_tree_lock` protects ordered extents.

`i_mmap_lock` participates in full-sync flag safety.

The VFS inode lock is required for certain runtime flags and reflink/fsync state transitions.

The header uses `READ_ONCE()` and `WRITE_ONCE()` for directory log index state.

## Risks And Edge Cases

On 32-bit systems, inode number handling is special to avoid truncating 64-bit Btrfs objectids.

Root stub inodes intentionally break normal root-reference assumptions and must be identified through `BTRFS_INODE_ROOT_STUB`.

Fsync correctness depends on interactions among `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `last_reflink_trans`, and runtime flags. Incorrect locking or stale updates can make fsync skip necessary work.

Compression eligibility must reject `NODATACOW` and `NODATASUM`.

`BTRFS_INODE_NO_DELALLOC_FLUSH` is a deadlock avoidance mechanism; setting/clearing it incorrectly can either deadlock or reduce flushing effectiveness.

## Testing Signals

Relevant tests should cover:
- 32-bit inode-number preservation.
- Fast vs full fsync transitions.
- Reflink followed by fsync and checksum logging.
- Root stub lookup through snapshot/subvolume nesting.
- Delalloc accounting and extent split/merge.
- NODATACOW/NODATASUM compression rejection.
- Encoded read/write paths.
- Verity enable serialization.
- Free-space inode special behavior.
