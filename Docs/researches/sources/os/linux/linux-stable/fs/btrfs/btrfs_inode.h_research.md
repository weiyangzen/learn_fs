# File Research: sources/os/linux/linux-stable/fs/btrfs/btrfs_inode.h

## Purpose

`btrfs_inode.h` defines the in-memory Btrfs inode structure, inode runtime flags, inode helper functions, inode creation argument structure, and the public inode-layer API used by Btrfs writeback, delalloc, checksums, VFS operations, fsync/logging, orphan handling, preallocation, encoded I/O, and inode lifecycle code.

## Runtime Flags

The anonymous enum defines `runtime_flags` bits for:

- `BTRFS_INODE_FLUSH_ON_CLOSE`: force ordered operation flushing on close after truncate-to-zero patterns.
- `BTRFS_INODE_DUMMY`: dummy inode state.
- `BTRFS_INODE_IN_DEFRAG`: inode is under defrag.
- `BTRFS_INODE_HAS_ASYNC_EXTENT`: async extent state exists.
- `BTRFS_INODE_NEEDS_FULL_SYNC`: inode must use full fsync; must be set under VFS inode lock except creation/loading contexts.
- `BTRFS_INODE_COPY_EVERYTHING`: fsync/logging copy-all state.
- `BTRFS_INODE_HAS_PROPS`: inode property cache exists.
- `BTRFS_INODE_SNAPSHOT_FLUSH`: snapshot-related flush state.
- `BTRFS_INODE_NO_XATTRS`: logged inode is known to have no xattrs until a new xattr is added.
- `BTRFS_INODE_NO_DELALLOC_FLUSH`: prevents flushing this inode's delalloc while holding dirty range locks and starting a transaction.
- `BTRFS_INODE_VERITY_IN_PROGRESS`: serializes verity enablement.
- `BTRFS_INODE_FREE_SPACE_INODE`: marks free-space cache inodes.
- `BTRFS_INODE_NO_CAP_XATTR`: marks absence of capability xattrs.
- `BTRFS_INODE_COW_WRITE_ERROR`: records COW/writeback error so fast fsync waits for ordered extents and avoids logging unwritten extent maps.
- `BTRFS_INODE_ROOT_STUB`: marks a synthetic directory inode for a subvolume entry without a root reference from the current snapshot.

## `struct btrfs_inode`

Major fields include:

- Identity:
  - `root`
  - `objectid` on 32-bit systems
  - embedded `vfs_inode`
- Compression and defrag:
  - `prop_compress`
  - `defrag_compress`
  - `defrag_compress_level`
- Core lock:
  - `lock` protects transaction/log counters, delalloc counters, disk size, outstanding extents, csum bytes, VFS byte updates, and file private data setup.
- Extent state:
  - `extent_tree`: cached extent maps.
  - `io_tree`: range state such as dirty, locked, delalloc.
  - `file_extent_tree`: tracks file extent item coverage when `NO_HOLES` is not enabled.
- Logging:
  - `log_mutex`
  - `last_trans`
  - `logged_trans`
  - `last_sub_trans`
  - `last_log_commit`
  - `last_unlink_trans`
  - `last_reflink_trans`
  - directory log index fields.
- Delalloc and ordered extents:
  - `outstanding_extents`
  - `ordered_tree_lock`
  - `ordered_tree`
  - `ordered_tree_last`
  - `delalloc_inodes`
  - `delalloc_bytes`
  - `new_delalloc_bytes`
  - `defrag_bytes`
  - `csum_bytes`
- File/directory size and indexing:
  - `disk_i_size`
  - `index_cnt`
  - `dir_index`
  - `first_dir_index_to_log`
  - `last_dir_index_offset`
- Relocation/root-stub unions:
  - `reloc_block_group_start`
  - `ref_root_id`
- Flags:
  - `runtime_flags`
  - persistent inode `flags`
  - `ro_flags`
- Reservation and delayed work:
  - embedded `block_rsv`
  - `delayed_node`
  - `delayed_iput`
- Metadata:
  - `generation`
  - creation time fields `i_otime_sec` and `i_otime_nsec`
  - `i_mmap_lock`

## Inline Helpers And Macros

- `BTRFS_DIR_START_INDEX` sets real directory entries to start at position 2 after `.` and `..`.
- `btrfs_get_first_dir_index_to_log()` and `btrfs_set_first_dir_index_to_log()` wrap `READ_ONCE`/`WRITE_ONCE`.
- `BTRFS_I()` is a type-checked, const-preserving conversion from VFS inode to Btrfs inode.
- `btrfs_inode_hash()` hashes an objectid/root pair.
- `btrfs_ino()` returns the 64-bit inode number, using `objectid` on 32-bit platforms except root stubs.
- `btrfs_get_inode_key()` fills a `BTRFS_INODE_ITEM_KEY`.
- `btrfs_set_inode_number()` updates both Btrfs and VFS inode numbers where needed.
- `btrfs_i_size_write()` updates VFS `i_size` and `disk_i_size`.
- `btrfs_is_free_space_inode()` and `is_data_inode()` classify special inodes.
- `btrfs_mod_outstanding_extents()` adjusts outstanding extent count and traces non-free-space inodes.
- `btrfs_set_inode_last_sub_trans()` records that writes happened in the current log transaction.
- `btrfs_set_inode_full_sync()` sets full-sync state and pessimistically updates `last_reflink_trans`.
- `btrfs_inode_in_log()` checks whether an inode is already logged for a generation and no newer subtransaction needs logging.
- `btrfs_inode_can_compress()` rejects compression for NODATACOW/NODATASUM inodes.
- `btrfs_assert_inode_locked()` asserts the VFS inode rwsem is held.
- `btrfs_update_inode_mapping_flags()` sets/clears stable writes based on NODATASUM.
- `btrfs_set_inode_mapping_order()` configures folio order range for data inodes when experimental support is enabled.

## Public Inode API Surface

The header declares APIs for:

- Checksums and read validation:
  - `btrfs_calculate_block_csum_folio()`
  - `btrfs_calculate_block_csum_pages()`
  - `btrfs_check_block_csum()`
  - `btrfs_data_csum_ok()`
- NOCOW and extents:
  - `can_nocow_extent()`
  - `btrfs_get_extent()`
  - `btrfs_create_io_em()`
  - `btrfs_get_extent_allocation_hint()`
- Delalloc/writeback:
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
- Directory and namespace operations:
  - `btrfs_lookup_dentry()`
  - `btrfs_set_inode_index()`
  - `btrfs_unlink_inode()`
  - `btrfs_add_link()`
  - `btrfs_delete_subvolume()`
- Inode creation:
  - `struct btrfs_new_inode_args`
  - `btrfs_new_inode_prepare()`
  - `btrfs_create_new_inode()`
  - `btrfs_new_inode_args_destroy()`
  - `btrfs_new_subvol_inode()`
- Truncate, expansion, and preallocation:
  - `btrfs_truncate_block()`
  - `btrfs_cont_expand()`
  - `btrfs_prealloc_file_range()`
  - `btrfs_prealloc_file_range_trans()`
- Lifecycle/cache:
  - `btrfs_evict_inode()`
  - `btrfs_alloc_inode()`
  - `btrfs_destroy_inode()`
  - `btrfs_free_inode()`
  - `btrfs_drop_inode()`
  - `btrfs_init_cachep()`
  - `btrfs_destroy_cachep()`
  - `btrfs_iget_path()`
  - `btrfs_iget()`
  - `btrfs_find_first_inode()`
- Inode item/orphan/delayed iput:
  - `btrfs_update_inode()`
  - `btrfs_update_inode_fallback()`
  - `btrfs_orphan_add()`
  - `btrfs_orphan_cleanup()`
  - `btrfs_add_delayed_iput()`
  - `btrfs_run_delayed_iputs()`
  - `btrfs_wait_on_delayed_iputs()`
- Encoded I/O:
  - `btrfs_encoded_io_compression_from_extent()`
  - `btrfs_encoded_read_regular_fill_pages()`
  - `btrfs_encoded_read()`
  - `btrfs_encoded_read_regular()`
  - `btrfs_do_encoded_write()`
- Locking and accounting:
  - `btrfs_inode_lock()`
  - `btrfs_inode_unlock()`
  - `btrfs_update_inode_bytes()`
  - `btrfs_assert_inode_range_clean()`
- Dentry integration:
  - `btrfs_dentry_operations`

## `struct btrfs_new_inode_args`

This structure groups inode creation inputs and prepared outputs:

- Inputs:
  - parent directory inode
  - dentry
  - new inode
  - orphan flag
  - subvolume flag
- Prepared outputs:
  - default ACL
  - ACL
  - fscrypt name

It separates pre-transaction preparation from transaction-time inode creation.

## Dependencies

This header sits at the boundary between Btrfs and VFS/MM infrastructure. It depends on Linux inode, mapping, mm, fscrypt, locking, trace, and ACL types, plus Btrfs ctree, block reserve, extent map, and extent I/O tree definitions.

It connects to Btrfs subsystems including transactions, ordered extents, checksums, extent maps, delalloc, tree log, orphan items, delayed inode/items, free-space cache inodes, encoded I/O, fscrypt, verity, and subvolume roots.

## Risks And Invariants

- Many fields in `struct btrfs_inode` are protected by `inode->lock`; direct unsynchronized access risks stale values and KCSAN reports.
- `BTRFS_INODE_NEEDS_FULL_SYNC` must be set under the correct locks to avoid races where fsync starts fast and later needs full sync.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` prevents deadlocks when transaction reservation could otherwise flush the same inode/range whose locks are already held.
- `disk_i_size` and VFS `i_size` intentionally differ during ordered writeback; helpers must preserve ordered-data semantics.
- 32-bit inode numbers require special handling through `objectid` to avoid truncation.
- Root stub inodes represent missing root references from snapshot contexts and must not be treated like normal subvolume root references.
- Compression eligibility must respect NODATACOW/NODATASUM flags to avoid checksum and COW semantic violations.
- Outstanding extent, delalloc, csum, and qgroup accounting is distributed across inode writeback and transaction code, so helper usage matters for ENOSPC correctness.
