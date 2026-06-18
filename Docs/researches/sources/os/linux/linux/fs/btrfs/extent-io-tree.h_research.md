# File Research: sources/os/linux/linux/fs/btrfs/extent-io-tree.h

## Purpose

`extent-io-tree.h` defines the Btrfs extent state bit model, owner types, core data structures, and public API for byte-range state tracking.

## State Bits

The enum defines many range-state flags, including:

- `EXTENT_DIRTY`
- `EXTENT_LOCKED`
- `EXTENT_DIO_LOCKED`
- `EXTENT_DELALLOC`
- `EXTENT_DEFRAG`
- `EXTENT_BOUNDARY`
- `EXTENT_NODATASUM`
- `EXTENT_NORESERVE`
- `EXTENT_QGROUP_RESERVED`
- `EXTENT_DELALLOC_NEW`
- `EXTENT_FINISHING_ORDERED`
- `EXTENT_ADD_INODE_BYTES`
- `EXTENT_CLEAR_ALL_BITS`
- `EXTENT_NOWAIT`

Control masks:

- `EXTENT_DO_ACCOUNTING`
- `EXTENT_CTLBITS`
- `EXTENT_LOCK_BITS`

Device allocation aliases:

- `CHUNK_ALLOCATED`
- `CHUNK_TRIMMED`
- `CHUNK_STATE_MASK`

## Tree Owners

The owner enum identifies how a tree is used:

- pinned extents
- excluded extents
- btree inode I/O
- regular inode I/O
- relocation blocks
- transaction dirty pages
- root dirty log pages
- inode file extents
- log csum ranges
- selftests
- device allocation state

Owner identity controls whether the tree stores `fs_info` directly or an inode pointer and whether inode delalloc hooks apply.

## Core Structures

`struct extent_io_tree` contains:

- RB-tree root
- `fs_info` or inode owner pointer
- owner id
- spinlock

`struct extent_state` contains:

- inclusive start/end
- RB-tree node
- waitqueue
- refcount
- state bitmask
- optional debug leak-list node

## Public API

Lifecycle:

- `btrfs_extent_io_tree_init()`
- `btrfs_extent_io_tree_release()`
- `btrfs_extent_state_init_cachep()`
- `btrfs_extent_state_free_cachep()`
- `btrfs_free_extent_state()`

Locking:

- `btrfs_lock_extent_bits()`
- `btrfs_try_lock_extent_bits()`
- `btrfs_lock_extent()`
- `btrfs_try_lock_extent()`
- `btrfs_unlock_extent()`
- `btrfs_lock_dio_extent()`
- `btrfs_try_lock_dio_extent()`
- `btrfs_unlock_dio_extent()`

Bit mutation:

- `btrfs_set_extent_bit()`
- `btrfs_clear_extent_bit_changeset()`
- `btrfs_clear_extent_bit()`
- `btrfs_clear_extent_dirty()`
- `btrfs_convert_extent_bit()`
- `btrfs_set_record_extent_bits()`
- `btrfs_clear_record_extent_bits()`

Queries:

- `btrfs_count_range_bits()`
- `btrfs_test_range_bit()`
- `btrfs_test_range_bit_exists()`
- `btrfs_get_range_bits()`
- `btrfs_find_first_extent_bit()`
- `btrfs_find_first_clear_extent_bit()`
- `btrfs_find_contiguous_extent_bit()`
- `btrfs_find_delalloc_range()`
- `btrfs_next_extent_state()`

Owner conversion:

- `btrfs_extent_io_tree_to_inode()`
- `btrfs_extent_io_tree_to_fs_info()`

## Integration Points

This header is used widely by Btrfs metadata, inode I/O, transaction, free-space, block-group, log, qgroup, and device-allocation code.

## Invariants

- Range end values in `extent_state` are inclusive.
- `EXTENT_NOWAIT` is a control bit and must be masked out before normal state manipulation.
- Device allocation trees reuse some extent-state bits with different names and must not use lock/boundary/accounting bits with special mutation semantics.
- Cached `extent_state` pointers are refcounted and must be released.
