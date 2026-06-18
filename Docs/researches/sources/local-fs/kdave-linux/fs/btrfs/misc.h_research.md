# File Research: sources/local-fs/kdave-linux/fs/btrfs/misc.h

## Purpose

`misc.h` provides small shared utility macros and inline helpers for Btrfs code: cleanup pointer helpers, enum bit construction, bio iteration, conditional wakeups, percentage math, 64-bit power-of-two checks, simple rb-tree helpers, and bitmap range tests.

## Key Utilities

`AUTO_KFREE()` and `AUTO_KVFREE()` define cleanup-at-scope-exit pointers initialized to `NULL`.

`ENUM_BIT()` creates enum-backed bit values with an auto-incremented internal sequence.

Bio helpers include:

- `bio_iter_phys()`
- `btrfs_bio_for_each_block()`
- `bio_get_size()`
- `init_bvec_iter_for_bio()`
- `btrfs_bio_for_each_block_all()`

These support block-sized iteration across bios, including large folios and highmem.

Waitqueue helpers:

- `cond_wake_up()` uses `wq_has_sleeper()` and carries the implied barrier.
- `cond_wake_up_nomb()` uses `waitqueue_active()` when a preceding barrier already exists.

Math/helpers:

- `mult_perc()`
- `is_power_of_two_u64()`
- `has_single_bit_set()`

The simple rb-tree helpers assume embedded structs begin with `struct rb_simple_node`, containing an rb node and `bytenr`. They implement exact search, first-at-or-after search, compare, and insert.

Bitmap helpers test whether a range is all set or all zero.

## Dependencies and Integration

This file pulls in common kernel headers for bios, rbtree, bitmap, waitqueues, pagemap, and math. It is used by ordered-data allocation flag validation and many lower-level Btrfs routines.

## Risk Notes

The rb-tree helpers depend on strict struct layout conventions. `cond_wake_up_nomb()` must only be used when callers truly provide the required memory barrier elsewhere.
