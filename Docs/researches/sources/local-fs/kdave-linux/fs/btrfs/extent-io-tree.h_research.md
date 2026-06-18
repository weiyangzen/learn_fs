# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.h

## Role

Defines Btrfs extent I/O tree state bits, owners, core data structures, and public APIs for range state tracking, locking, state transitions, and queries.

## State Bits

The extent-state bit enum includes:

- Dirty/writeback-related state: `EXTENT_DIRTY`.
- Locking state: `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`.
- Tree-log dirty tracking: `EXTENT_DIRTY_LOG1`, `EXTENT_DIRTY_LOG2`.
- Delalloc and writeback accounting: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_ADD_INODE_BYTES`.
- Defrag and boundary markers: `EXTENT_DEFRAG`, `EXTENT_BOUNDARY`.
- Data checksum/reservation/accounting flags: `EXTENT_NODATASUM`, `EXTENT_CLEAR_META_RESV`, `EXTENT_NORESERVE`, `EXTENT_QGROUP_RESERVED`, `EXTENT_CLEAR_DATA_RESV`.
- Wait and ordered-completion flags: `EXTENT_NEED_WAIT`, `EXTENT_FINISHING_ORDERED`.
- Control-only flags: `EXTENT_CLEAR_ALL_BITS` and `EXTENT_NOWAIT`.

Derived masks:

- `EXTENT_DO_ACCOUNTING` combines metadata/data reservation clear bits.
- `EXTENT_CTLBITS` identifies control bits that are not persisted as normal state.
- `EXTENT_LOCK_BITS` combines regular and direct-I/O range locks.

## Device Allocation Aliases

The header reuses extent-state bits for device allocation trees:

- `CHUNK_ALLOCATED` maps to `EXTENT_DIRTY`.
- `CHUNK_TRIMMED` maps to `EXTENT_DEFRAG`.
- `CHUNK_STATE_MASK` covers both. The comment warns that lock/boundary/accounting bits are avoided because bit manipulation functions attach special behavior to them.

## Tree Owners

Owner IDs identify the semantic owner of each extent I/O tree:

- Filesystem-wide pinned and excluded extents.
- Btree inode I/O and regular inode I/O.
- Relocation blocks.
- Transaction dirty pages.
- Root dirty log pages.
- Inode file extents.
- Log checksum ranges.
- Selftests.
- Device allocation state.

The owner determines whether the tree's union pointer is interpreted as `fs_info` or `inode`, and whether inode delalloc accounting hooks run.

## Data Structures

- `struct extent_io_tree` contains the rb-root, owner union (`fs_info` or `inode`), owner byte, and spinlock.
- `struct extent_state` contains inclusive range start/end, rb-node, wait queue, refcount, state bitmask, and optional debug leak-list linkage.

## API Surface

- Tree lifecycle and mapping: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, `btrfs_extent_io_tree_to_inode()`, `btrfs_extent_io_tree_to_fs_info()`.
- Cache lifecycle: `btrfs_extent_state_init_cachep()`, `btrfs_extent_state_free_cachep()`, `btrfs_free_extent_state()`.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`, inline regular lock/unlock helpers, and inline DIO lock/unlock helpers.
- Counting and testing: `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`.
- Setting/clearing/converting: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, inline `btrfs_clear_extent_bit()`, `btrfs_clear_record_extent_bits()`, inline `btrfs_clear_extent_dirty()`, and `btrfs_convert_extent_bit()`.
- Searching: `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`.
- Iteration: `btrfs_next_extent_state()`.

## Research Notes

This header is the contract for a reusable Btrfs range-state abstraction. The state bit definitions encode both ordinary extent state and command/control behavior, so callers must be careful to use the right helper: lock bits imply exclusivity and wait queues, accounting bits trigger inode/block reservation side effects, and `EXTENT_NOWAIT` changes allocation behavior rather than becoming persistent state.
