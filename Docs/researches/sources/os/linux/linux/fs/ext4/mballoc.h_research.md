# File Research: sources/os/linux/linux/fs/ext4/mballoc.h

## Purpose

Declares ext4 multiblock allocator data structures, defaults, helper functions, query callback types, and KUnit test entry points shared by `mballoc.c` and ext4 internals.

## Key Defaults and Constants

- `MB_DEFAULT_MAX_TO_SCAN`: default maximum found extents to scan before settling.
- `MB_DEFAULT_MIN_TO_SCAN`: minimum found extents to inspect for a good fit.
- `MB_DEFAULT_STATS`: default allocator stats collection setting.
- `MB_DEFAULT_STREAM_THRESHOLD`: small-file stream/locality threshold.
- `MB_DEFAULT_ORDER2_REQS`: minimum order for buddy power-of-two search.
- `MB_DEFAULT_GROUP_PREALLOC`: default group preallocation length.
- `MB_DEFAULT_LINEAR_LIMIT`: rotational-device linear group scan limit before optimized scan.
- `MB_DEFAULT_LINEAR_SCAN_THRESHOLD`: minimum groups for scan optimization.
- `MB_DEFAULT_BEST_AVAIL_TRIM_ORDER`: max trim order for best-available allocation.
- `MB_NUM_ORDERS(sb)`: valid buddy order count derived from block size.

## Main Structures

`struct ext4_free_data`
- Tracks clusters freed by a transaction but not yet reusable.
- Linked both globally through `efd_list` and per group through `efd_node`.
- Stores group, start cluster, count, and freeing transaction id.

`struct ext4_prealloc_space`
- Represents inode or locality-group preallocation.
- Uses an rbtree node for inode PAs or list node for locality PAs.
- Also links into the block group's PA list.
- Tracks physical start, logical start, length, free count, type, deletion state, reference count, and owner lock.

`struct ext4_free_extent`
- Describes an allocator extent: logical block, group-relative cluster start, group, and cluster length.

`struct ext4_locality_group`
- Per-CPU small-file preallocation context.
- Contains a mutex and hash buckets of group PAs by remaining free length order.

`struct ext4_allocation_context`
- Per-allocation working state.
- Stores original, normalized goal, best-found, and final extents.
- Tracks scan stats, criteria, status, flags, prefetch state, PA pointer, locality group, and pinned buddy folios.

`struct ext4_buddy`
- Loaded view of one block group’s buddy and bitmap folios plus group info and superblock.

## Helpers

- `ext4_grp_offs_to_block()` converts group-relative cluster offset to physical block.
- `extent_logical_end()` computes logical end of a free extent using cluster-to-block conversion.
- `pa_logical_end()` computes logical end of a preallocation descriptor.
- `ext4_mballoc_query_range_fn` defines callbacks for free-range iteration.

## External Interfaces

- `ext4_mballoc_query_range()` iterates free extents in a group.
- `ext4_mb_mark_context()` updates block bitmap/group descriptor state and optionally reports changed clusters.
- KUnit-only declarations expose selected internal allocator primitives for ext4 tests.

## Research Notes

This header captures allocator state contracts rather than policy. The important correctness details are PA ownership/lifetime fields, cluster-unit vs block-unit conversions, and `ac_*` extent roles in `ext4_allocation_context`.
