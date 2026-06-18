# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.c

This file implements Btrfs delayed back reference tracking. It queues extent reference count changes and extent operations for later processing, reducing immediate extent-tree churn and avoiding deep update chains during btree modifications.

Core data model:
- Delayed ref heads are stored in an xarray keyed by logical bytenr shifted by `sectorsize_bits`.
- Each head represents one extent and owns an rbtree of delayed ref nodes.
- Ref nodes are sorted by ref type, parent/root identity, data ref fields, and sequence.
- Add refs are also linked into `ref_add_list` to prioritize additions before drops.
- Dirty qgroup extent records are tracked in a separate xarray.

Reservation accounting:
- `btrfs_check_space_for_delayed_refs()` compares delayed refs reserve size against delayed refs plus global reserve.
- `btrfs_delayed_refs_rsv_release()` drops delayed ref and csum deletion reservation units.
- `btrfs_update_delayed_refs_rsv()` moves pending per-transaction delayed ref/csum reservation demand into `fs_info->delayed_refs_rsv`, preferentially taking bytes from `trans->delayed_rsv`.
- Block group insert/update helpers adjust delayed refs reserve size for block group item operations.
- `btrfs_delayed_refs_rsv_refill()` reserves metadata bytes up to one delayed ref unit at a time and handles racing refillers.
- Zoned filesystems cap delayed refs reservation to half of usable metadata space via `btrfs_zoned_cap_metadata_reservation()`.

Comparison and merging:
- `comp_data_refs()` compares data refs by inode objectid and offset.
- `comp_refs()` compares full delayed ref identity.
- `tree_insert()` inserts into the per-head rbtree.
- `merge_ref()` collapses adjacent compatible refs with opposite or same actions, dropping zero-mod refs.
- `btrfs_merge_delayed_refs()` skips data refs, respects tree mod log sequence constraints, and repeatedly merges metadata refs.
- `btrfs_check_delayed_seq()` prevents running refs still needed by tree-mod-log readers.

Head selection:
- `btrfs_select_ref_head()` scans `head_refs` from `run_delayed_start`, skips processing heads, marks a selected head processing, decrements ready count, and locks the head mutex.
- `btrfs_unselect_ref_head()` clears processing and returns the head to ready state.
- `btrfs_delete_ref_head()` removes a head from xarray tracking and adjusts global counts.
- `btrfs_select_delayed_ref()` chooses add refs first, then the first rbtree ref.

Insertion:
- `init_delayed_ref_common()` initializes a ref node from generic `struct btrfs_ref`, including tree mod sequence for fs trees.
- `init_delayed_ref_head()` initializes the head, ref count delta, reserved bytes, data/system flags, level, qgroup record fields, and `must_insert_reserved` state.
- `add_delayed_ref_head()` inserts or updates a head, traces qgroup extent records, updates csum deletion reservation demand for data drops, and tracks head counts.
- `insert_delayed_ref()` inserts a ref node or merges it into an existing matching node.
- `add_delayed_ref()` allocates node/head/qgroup record, reserves xarray entries, initializes state, inserts both head and node under delayed refs lock, updates reserve accounting, and posts qgroup tracing.
- `btrfs_add_delayed_tree_ref()` and `btrfs_add_delayed_data_ref()` are typed wrappers.
- `btrfs_add_delayed_extent_op()` attaches delayed extent operation updates to an existing or new head without adding an individual ref.

Reference/query helpers:
- `btrfs_init_tree_ref()` initializes metadata refs and qgroup skip policy.
- `btrfs_init_data_ref()` initializes data refs and qgroup skip policy.
- `btrfs_find_delayed_ref_head()` looks up a head under delayed refs lock.
- `btrfs_find_delayed_tree_ref()` checks whether a matching tree ref add exists under a head.
- `btrfs_put_delayed_ref()` releases delayed ref node refs.

Abort cleanup:
- `btrfs_destroy_delayed_refs()` walks all heads, locks each, drops every pending ref node, frees delayed extent ops, deletes heads, and handles special accounting for `must_insert_reserved`.
- If a reserved extent was never inserted, cleanup may pin bytes in the block group and call `btrfs_error_unpin_extent_range()`.
- Qgroup extent records are destroyed after delayed refs are drained.

Slab lifecycle:
- `btrfs_delayed_ref_init()` creates slab caches for heads, nodes, and delayed extent ops.
- `btrfs_delayed_ref_exit()` destroys them.

Important invariants:
- `delayed_refs->lock` protects xarrays and global counts.
- `head->lock` protects the per-head rbtree and add list.
- `head->mutex` serializes running refs for a single extent.
- Add refs run before drop refs to avoid transient deletion of extent items that still need new refs.
- Xarray keys use shifted bytenr to fit 32-bit indexes better and produce denser index space.
