# File Research: sources/os/linux/linux/fs/btrfs/delayed-ref.c

This file implements delayed back reference tracking. Btrfs queues extent reference count changes and extent metadata operations in memory, then processes them later so btree modifications do not immediately recurse into extent-tree updates.

Core data model:
- A transaction’s `btrfs_delayed_ref_root` stores delayed ref heads in an xarray keyed by logical bytenr shifted by `sectorsize_bits`.
- Each `btrfs_delayed_ref_head` represents one extent, stores aggregate reference modification counts, and owns an rbtree of individual delayed ref nodes.
- Individual refs are ordered by ref type, root/parent identity, data ref fields, and sequence number.
- Add refs are also linked in `head->ref_add_list` so additions can be selected before drops, avoiding premature extent item deletion.
- Qgroup dirty extent records are tracked in `delayed_refs->dirty_extents`.

Reservation accounting:
- `btrfs_check_space_for_delayed_refs()` checks whether delayed refs pressure exceeds delayed refs plus global reserve.
- `btrfs_delayed_refs_rsv_release()` releases metadata reserve units for delayed refs and checksum deletions.
- `btrfs_update_delayed_refs_rsv()` transfers pending transaction delayed-ref and csum-deletion accounting into `fs_info->delayed_refs_rsv`, preferentially consuming bytes already held in the transaction local delayed reserve.
- Block group insert/update helpers adjust delayed refs reserve size for block group item maintenance.
- `btrfs_delayed_refs_rsv_refill()` refills the reserve up to one delayed-ref metadata unit at a time and releases excess bytes if another task raced and filled it first.
- Zoned filesystems use `btrfs_zoned_cap_metadata_reservation()` to avoid letting delayed refs reserve exceed half of usable metadata space.

Merging and selection:
- `comp_refs()` and related helpers compare delayed refs for ordering and merge eligibility.
- `insert_delayed_ref()` inserts a new ref into a head rbtree or merges it with an equivalent existing ref, cancelling opposite actions when ref counts balance to zero.
- `btrfs_merge_delayed_refs()` performs additional metadata ref merging while respecting the tree mod log’s lowest sequence.
- `btrfs_select_ref_head()` finds the next unprocessed head, marks it processing, advances `run_delayed_start`, and locks the head safely even if the spinlock must be dropped.
- `btrfs_unselect_ref_head()` clears processing state and restores readiness.
- `btrfs_select_delayed_ref()` chooses add refs before other refs for a head.

Adding refs:
- `init_delayed_ref_head()` initializes aggregate head state, including `must_insert_reserved`, data/system flags, owning root, csum deletion tracking basis, and qgroup record fields.
- `add_delayed_ref_head()` inserts or updates the xarray head, traces qgroup extents, maintains `num_heads` and `num_heads_ready`, and accounts pending csum deletion reservations.
- `init_delayed_ref_common()` initializes an individual ref node and captures a tree-mod sequence for filesystem tree refs.
- `btrfs_init_tree_ref()` and `btrfs_init_data_ref()` populate generic ref fields and decide whether qgroup accounting can be skipped.
- `btrfs_add_delayed_tree_ref()` and `btrfs_add_delayed_data_ref()` allocate and queue metadata or data refs.
- `btrfs_add_delayed_extent_op()` attaches or merges an extent operation into the delayed ref head without adding a normal ref node.

Lookup and destruction:
- `btrfs_find_delayed_ref_head()` looks up a head under delayed refs lock.
- `btrfs_find_delayed_tree_ref()` searches a head for an add reference matching a root or parent.
- `btrfs_destroy_delayed_refs()` drains all heads during transaction cleanup/abort, drops all refs, frees delayed extent ops, deletes heads from the xarray, pins reserved extents when needed, performs ref-head accounting cleanup, and destroys qgroup extent records.

Important invariants:
- Head xarray indexes are sector-shifted to be dense and workable on 32-bit platforms.
- A head’s `total_ref_mod` is not decremented as refs run; it records the total modification needed for qgroup/checksum accounting decisions.
- A head’s `ref_mod` is adjusted as refs run so on-disk reference count plus outstanding modifications remains meaningful.
- Add refs must be processed before drop refs for the same head to avoid deleting extent items that later additions still need.
