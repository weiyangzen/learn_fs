# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.h

## Purpose
Declares Btrfs extent IO tree data structures, state bits, owner IDs, and public APIs for range state tracking.

## State Bits
Defines range-state bits including:
- IO/writeback state: `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`.
- Logging and delalloc state: `EXTENT_DIRTY_LOG1`, `EXTENT_DIRTY_LOG2`, `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`.
- Range modifiers/accounting: `EXTENT_BOUNDARY`, `EXTENT_NODATASUM`, `EXTENT_NORESERVE`, `EXTENT_QGROUP_RESERVED`.
- Reservation cleanup/control: `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_ADD_INODE_BYTES`, `EXTENT_CLEAR_ALL_BITS`.
- Ordered completion marker: `EXTENT_FINISHING_ORDERED`.
- Allocation behavior control: `EXTENT_NOWAIT`, which must remain last and is masked out before storing state.

## Bit Masks And Aliases
- `EXTENT_DO_ACCOUNTING`: reservation cleanup bits.
- `EXTENT_CTLBITS`: control bits not stored as persistent extent state.
- `EXTENT_LOCK_BITS`: lock-bit group.
- Device allocation tree aliases:
  - `CHUNK_ALLOCATED = EXTENT_DIRTY`
  - `CHUNK_TRIMMED = EXTENT_DEFRAG`
  - `CHUNK_STATE_MASK` combines both.

## Tree Owners
Enumerates owner IDs for pinned extents, excluded extents, btree inode IO, inode IO, relocation blocks, transaction dirty pages, root log dirty pages, inode file extents, log checksum ranges, selftests, and device allocation state.

## Main Structures
- `struct extent_io_tree`: rb root, owner tag, spinlock, and union of `fs_info`/`inode` depending on owner.
- `struct extent_state`: inclusive start/end, rb node, waitqueue, refcount, state bits, and optional debug leak-list node.

## Public APIs
- Initialization/release: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, slab cache init/free.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`, inline normal and DIO lock/unlock wrappers.
- Set/clear/convert: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, inline `btrfs_clear_extent_bit()`, inline `btrfs_clear_extent_dirty()`, `btrfs_clear_record_extent_bits()`, `btrfs_convert_extent_bit()`.
- Queries/iteration: `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`, `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`, `btrfs_next_extent_state()`.
- Type conversion helpers: `btrfs_extent_io_tree_to_inode()`, `btrfs_extent_io_tree_to_fs_info()`.

## Notes
The header establishes the contract that many stored bits have semantic side effects in the implementation, especially lock bits, delalloc accounting bits, and control bits. Callers must use the wrappers rather than directly mutating tree state.
