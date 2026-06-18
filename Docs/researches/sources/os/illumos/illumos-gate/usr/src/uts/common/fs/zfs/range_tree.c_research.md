# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/range_tree.c

## Scope

This file implements ZFS range trees, the extent set data structure used for free-space, deferred-free, allocation, trim, checkpoint, and other range accounting. It supports 32-bit, 64-bit, and gap-bridging segment encodings, btree storage, histograms, callbacks, walking/vacating, and set-difference style updates. The file was read completely.

## APIs And Entry Points

- Lifecycle: `range_tree_create()`, `range_tree_create_impl()`, `range_tree_destroy()`.
- Mutation: `range_tree_add()`, `range_tree_remove()`, `range_tree_remove_fill()`, `range_tree_clear()`, `range_tree_resize_segment()`, `range_tree_adjust_fill()`, `range_tree_swap()`, `range_tree_vacate()`.
- Queries/walks: `range_tree_find()`, `range_tree_contains()`, `range_tree_find_in()`, `range_tree_verify_not_present()`, `range_tree_walk()`, `range_tree_first()`, `range_tree_space()`, `range_tree_numsegs()`, `range_tree_is_empty()`, `range_tree_min()`, `range_tree_max()`, `range_tree_span()`.
- Verification and auxiliary btrees: `range_tree_stat_verify()`, `rt_btree_ops`.
- Delta operations: `range_tree_remove_xor_add_segment()`, `range_tree_remove_xor_add()`.

## Control Flow

A range tree stores non-overlapping segments in a `zfs_btree_t`. Adding a range finds adjacent or gap-near neighbors, merges with before/after segments when appropriate, updates fill counts for gap trees, adjusts histograms, invokes callbacks, and increments total represented space. Removing a range finds the containing segment, then deletes, shortens, or splits it while updating callbacks, histograms, and total space.

Gap trees bridge small holes between nearby ranges for scan-style I/O grouping. For these trees, fill can be less than segment span, and removals are restricted to complete segments unless `range_tree_remove_fill()` is adjusting fill. Normal trees require fill to equal extent size.

Callbacks in `range_tree_ops_t` allow users to maintain secondary structures such as a size-sorted btree. `rt_btree_ops` is the generic implementation for mirroring range-tree segments into another btree. `metaslab.c` provides its own callback set to maintain size-sorted allocation trees with a minimum segment-size floor.

`range_tree_remove_xor_add()` is used for log spacemap unflushed delta handling: each input segment removes overlapping portions from one tree and adds non-overlapping leftovers to another, effectively applying XOR-like alloc/free cancellation.

## State And Dependencies

Each `range_tree_t` contains a root btree, total `rt_space`, histogram buckets, optional ops/arg, segment type, logical start/shift for compact 32-bit encodings, optional btree comparator, and gap size. It depends on ZFS btrees, segment accessor macros, kmem allocation, panic/recovery helpers, and ZFS debug logging.

This file is foundational for `metaslab.c`; metaslab allocation correctness relies on range-tree merging/splitting, histogram accuracy, and callback updates.

## Risks And Invariants

- `rt_space` and histograms must match btree contents after every add/remove/split/merge. `range_tree_stat_verify()` exists to catch drift.
- Removing a non-existent segment calls `zfs_panic_recover()`, because that implies space accounting corruption.
- Gap trees have special fill semantics and cannot safely support arbitrary partial removals.
- Callback users must tolerate temporary remove/add sequences around resize, fill adjustment, split, merge, and vacate operations.
- `range_tree_vacate()` can either discard segments or walk them into another consumer while destroying btree nodes.
- Compact 32-bit segment trees rely on correct `start` and `shift` normalization from callers.

## Summary

`range_tree.c` supplies the extent algebra underneath ZFS allocator state. Its job is not policy; it provides precise merged ranges, accounting, histograms, and callback hooks that higher layers such as metaslabs use for allocation choice and sync-time persistence.
