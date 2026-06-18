# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/range_tree.h

This header declares ZFS range trees, the non-concurrent extent-set abstraction used by metaslabs, spacemaps, trim, checkpoints, and removal accounting.

Core definitions:
- `RANGE_TREE_HISTOGRAM_SIZE` is 64 buckets.
- `range_seg_type_t` supports compact 32-bit, 64-bit, and gap/fill segment forms.
- `range_tree_t` stores an offset-ordered `zfs_btree_t`, total represented space, segment encoding, start/shift normalization, optional callback ops/arg, optional secondary btree comparator, allowable gap, and size histogram.
- Segment structs include `range_seg32_t`, `range_seg64_t`, and `range_seg_gap_t`; `range_seg_max_t` is the stack-safe maximum representation.
- Inline accessors convert raw stored starts/ends/fill values to logical byte offsets with `rt_start` and `rt_shift`, and enforce alignment and 32-bit limits on mutation.
- `range_tree_ops_t` lets consumers mirror create/destroy/add/remove/vacate events into secondary structures.

Public API surface:
- Lifecycle: create, create implementation, destroy.
- Query: contains/find/find_in, first, min/max/span, space, number of segments, empty check, histogram verification.
- Mutation: add/remove/remove_fill/clear, resize, adjust fill, swap, vacate, walk.
- Delta helpers: `range_tree_remove_xor_add_segment()` and `range_tree_remove_xor_add()`.
- Built-in secondary btree callbacks are exported as `rt_btree_ops`.

Risk-sensitive invariants:
- Range trees are explicitly not internally synchronized; consumers provide external locking.
- All stored offsets and sizes must be aligned to `1 << rt_shift` and be at or above `rt_start`.
- For non-gap segment types, fill must equal segment length; gap trees have different fill semantics.
- Histograms and `rt_space` are allocator-critical and must track every add/remove/split/merge.
