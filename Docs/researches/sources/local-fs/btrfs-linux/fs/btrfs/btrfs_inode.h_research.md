# File Research: sources/local-fs/btrfs-linux/fs/btrfs/btrfs_inode.h

## Scope

This header defines the in-memory Btrfs inode structure, inode runtime flags, inode helper functions, and public inode-related APIs implemented across `inode.c` and related Btrfs files. It connects VFS inode state to Btrfs extent maps, extent I/O state, delalloc accounting, ordered extents, fsync log state, per-inode metadata reserves, delayed inode/iput handling, compression policy, and encoded I/O.

## Runtime Flags

The anonymous enum defines inode runtime flags including:

- `BTRFS_INODE_FLUSH_ON_CLOSE` for ordered close behavior after truncate/write.
- `BTRFS_INODE_DUMMY` and `BTRFS_INODE_ROOT_STUB` for special placeholder inodes.
- `BTRFS_INODE_IN_DEFRAG`, `BTRFS_INODE_HAS_ASYNC_EXTENT`, and `BTRFS_INODE_NEEDS_FULL_SYNC`.
- `BTRFS_INODE_COPY_EVERYTHING` and `BTRFS_INODE_HAS_PROPS`.
- `BTRFS_INODE_SNAPSHOT_FLUSH` for snapshot delalloc flushing.
- `BTRFS_INODE_NO_XATTRS` and `BTRFS_INODE_NO_CAP_XATTR` for log/xattr optimizations.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid self-deadlock when dirty pages and locked ranges would be flushed during transaction reservation.
- `BTRFS_INODE_VERITY_IN_PROGRESS`.
- `BTRFS_INODE_FREE_SPACE_INODE`.
- `BTRFS_INODE_COW_WRITE_ERROR` to force ordered extent wait/full fsync behavior after failed COW writeback.

## Main Data Structure

`struct btrfs_inode` embeds `struct inode vfs_inode` and adds Btrfs-specific state:

- Root identity: `root`, 32-bit-only `objectid`, and helpers for inode number/key.
- Compression policy: `prop_compress`, `defrag_compress`, and `defrag_compress_level`.
- Main spinlock protecting log counters, delalloc counters, disk size, outstanding extents, checksum bytes, VFS block usage, and file private-data setup.
- Extent state: `extent_tree`, `io_tree`, and optional `file_extent_tree`.
- Logging: `log_mutex`, `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `last_unlink_trans`, and `last_reflink_trans`.
- Delalloc and extent accounting: `outstanding_extents`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, and embedded `block_rsv`.
- Ordered data: `ordered_tree_lock`, `ordered_tree`, and cached last ordered rb-node.
- Directory-specific state: `index_cnt`, `dir_index`, `first_dir_index_to_log`, and `last_dir_index_offset`.
- Relocation/root-stub union state: `reloc_block_group_start` or `ref_root_id`.
- On-disk inode flags split into `flags` and `ro_flags`.
- Delayed infrastructure: `delayed_node`, `delayed_iput`.
- Creation time fields `i_otime_sec` and `i_otime_nsec`.
- `i_mmap_lock` for mmap/write coordination.

## Inline Helpers

- `btrfs_get_first_dir_index_to_log()` and `btrfs_set_first_dir_index_to_log()` use READ/WRITE_ONCE.
- `BTRFS_I()` is a type-checked, const-preserving container conversion from VFS inode.
- `btrfs_inode_hash()` hashes objectid and root objectid, with 32-bit folding on 32-bit platforms.
- `btrfs_ino()` returns a full 64-bit inode number, using `objectid` on 32-bit platforms except root stubs.
- `btrfs_get_inode_key()` builds the inode item key.
- `btrfs_set_inode_number()` updates both Btrfs objectid and VFS inode number as required.
- `btrfs_i_size_write()` updates VFS `i_size` and Btrfs `disk_i_size`.
- `btrfs_is_free_space_inode()` and `is_data_inode()` classify special inodes.
- `btrfs_mod_outstanding_extents()` updates outstanding extent count and emits trace events except for free-space inodes.
- `btrfs_set_inode_last_sub_trans()` records a file change against the root log transaction.
- `btrfs_set_inode_full_sync()` sets full fsync state and conservatively updates `last_reflink_trans`.
- `btrfs_inode_in_log()` checks whether an inode is already safely represented in the log.
- `btrfs_inode_can_compress()` rejects compression when NODATACOW or NODATASUM is set.
- `btrfs_assert_inode_locked()` checks VFS inode lock ownership.
- `btrfs_update_inode_mapping_flags()` toggles stable writes based on NODATASUM.
- `btrfs_set_inode_mapping_order()` configures folio order range under experimental block-size support.

## Declared API Surface

The header declares APIs for:

- Block checksum calculation and verification.
- Data checksum validation.
- NOCOW extent checks.
- Delalloc inode list management and delalloc extent state callbacks.
- Directory lookup, index allocation, link/unlink, subvolume deletion, and truncate-block handling.
- Delalloc flushing across roots and writeback ranges.
- New inode preparation, creation, destruction of args, and subvolume inode creation.
- Inode allocation/free/destroy/drop and cache slab init/teardown.
- Inode lookup by root/path and extent map lookup/creation.
- Inode item update and fallback update.
- Orphan add/cleanup, continuous expansion, delayed iput handling.
- Preallocation with or without an existing transaction.
- COW writepage fixup and delalloc range execution.
- Encoded read/write helpers and compressed encoded I/O.
- In-memory inode search by minimum inode number.
- Inode lock/unlock wrappers supporting shared, trylock, and mmap locking.
- Inode byte accounting and range-clean assertions.
- Extent allocation hinting and I/O extent-map creation.
- `btrfs_dentry_operations`.

## Dependencies And Consumers

The header depends on VFS/MM types, fscrypt, tracepoints, Btrfs ctree definitions, block reserves, extent maps, and extent I/O trees. It is consumed broadly by inode, file, ordered-data, extent I/O, direct I/O, ioctl, tree-log, relocation, free-space cache, verity, and directory operation code.

## Risks And Invariants

- Many `struct btrfs_inode` fields have mode-specific meanings through unions. Callers must only use file fields for files and directory fields for directories.
- `inode->lock` protects several independent-looking counters and fsync fields; updating them without the lock risks fsync/log replay bugs or accounting races.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` is a deadlock avoidance flag and must be set only around contexts that hold file-range locks while reserving transaction space.
- Full fsync marking must preserve reflink-related pessimism to avoid logging incomplete shared checksum/extents state.
- 32-bit inode number handling differs from 64-bit platforms and root stubs are a special case.
- `disk_i_size` and VFS `i_size` intentionally differ during ordered writeback; helpers should be used where both must move together.
- Free-space inodes suppress some tracing/accounting paths and have special behavior in block-group/free-space-cache code.
