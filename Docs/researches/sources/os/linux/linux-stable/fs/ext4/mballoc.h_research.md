# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc.h

## Purpose

Defines the private data structures, defaults, helper functions, and test-facing declarations for ext4's multiblock allocator.

## Main Responsibilities

- Provide allocator tuning defaults for scan lengths, stream thresholds, order-2 requests, group preallocation, linear scanning, and best-available trimming.
- Define the core allocator records used by `mballoc.c`: pending freed extents, preallocation descriptors, free extents, locality groups, allocation contexts, and loaded buddy handles.
- Define PA types for inode-specific and group/locality preallocations.
- Provide inline helpers for converting group offsets to filesystem blocks and computing logical end positions.
- Declare the free-space query callback API and bitmap-marking API.
- Expose KUnit test wrappers when ext4 KUnit tests are enabled.

## Key Structures

- `struct ext4_free_data` describes clusters freed by a transaction but not yet available for reuse. It is linked both globally by transaction list and per group by rb tree.
- `struct ext4_prealloc_space` describes reserved but not necessarily consumed clusters. It can be linked into an inode rbtree or locality-group list, always appears on a group PA list, and carries lock/reference/deletion state.
- `struct ext4_free_extent` describes a candidate or selected free extent in cluster units, with logical block context for file allocations.
- `struct ext4_locality_group` is a per-CPU grouping object with a mutex and PA buckets keyed by free-space order.
- `struct ext4_allocation_context` holds the original, goal, best, and found extents plus scan state, flags, prefetch state, selected PA, locality group, and pinned buddy/bitmap folios.
- `struct ext4_buddy` packages loaded buddy bitmap state for one group.

## Important Interfaces

- `ext4_grp_offs_to_block()` converts an `ext4_free_extent` group/cluster offset to physical filesystem block.
- `extent_logical_end()` and `pa_logical_end()` compute logical range ends with `loff_t` to avoid overflow.
- `ext4_mballoc_query_range()` iterates free extents in a block group for fsmap-style callers.
- `ext4_mb_mark_context()` marks allocation bitmap state and updates counters/checksums.
- Test exports cover bit operations, simple replay allocation, diskspace marking, buddy generation/loading/unloading, buddy mark/free, and simple free helpers.

## Dependencies

- Includes ext4 core and journaling headers plus kernel filesystem, quota, buffer-head, procfs, seq_file, block-device, mutex, page-cache, and swap headers.
- Consumed primarily by `mballoc.c`, with query and marking interfaces used by other ext4 subsystems.

## Research Notes

The header makes the allocator's unit split explicit: free extents and PA lengths are in clusters, while public block interfaces often convert to filesystem blocks. The allocation context mirrors the allocator pipeline: original request, normalized goal, best candidate, final allocation, scan criteria, and PA/buddy resources.
