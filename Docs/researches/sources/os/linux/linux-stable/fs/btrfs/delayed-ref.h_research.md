# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.h

This header defines delayed extent-reference data structures, reservation helpers, and the API used by extent-tree and transaction code.

Core enums:
- `enum btrfs_delayed_ref_action`
  - `BTRFS_ADD_DELAYED_REF`
  - `BTRFS_DROP_DELAYED_REF`
  - `BTRFS_ADD_DELAYED_EXTENT`
  - `BTRFS_UPDATE_DELAYED_HEAD`
- `enum btrfs_delayed_ref_flags`
  - `BTRFS_DELAYED_REFS_FLUSHING`
- `enum btrfs_ref_type`
  - `BTRFS_REF_NOT_SET`
  - `BTRFS_REF_DATA`
  - `BTRFS_REF_METADATA`

Reference payloads:
- `struct btrfs_data_ref`
  - Referring inode objectid and file-relative offset.
- `struct btrfs_tree_ref`
  - Tree block level.

Core structures:
- `struct btrfs_delayed_ref_node`
  - Individual delayed ref operation in a head rbtree.
  - Tracks bytenr, length, sequence, ref root, parent, refcount, ref_mod, action, key type, and data/tree payload.
- `struct btrfs_delayed_extent_op`
  - Pending extent item key/flag updates.
- `struct btrfs_delayed_ref_head`
  - Per-extent aggregate state and processing lock.
  - Tracks total/current ref_mod, reserved bytes, owning root, level, data/system flags, processing/tracked state, extent op, and per-head rbtree/list.
- `struct btrfs_delayed_ref_root`
  - Transaction-level delayed refs state.
  - Tracks head refs, dirty extents, counters, pending csums, flags, scan position, and qgroup skip root.
- `struct btrfs_ref`
  - Generic ref initializer used by callers before queueing delayed refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` calculates metadata reservation for delayed refs and doubles it when free-space tree updates are needed.
- `btrfs_calc_delayed_ref_csum_bytes()` calculates metadata needed for csum deletion.
- `btrfs_alloc_delayed_extent_op()` and `btrfs_free_delayed_extent_op()` manage extent-op cache objects.
- `btrfs_ref_head_to_space_flags()` maps a ref head to data/system/metadata block group flags.
- `btrfs_put_delayed_ref_head()` drops head references.
- `btrfs_delayed_ref_unlock()` unlocks a head mutex.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose owner/offset fields by ref kind.
- `btrfs_ref_type()` maps generic refs to Btrfs extent-tree key types.

Public API:
- Initialization:
  - `btrfs_delayed_ref_init()`
  - `btrfs_delayed_ref_exit()`
- Generic ref setup:
  - `btrfs_init_tree_ref()`
  - `btrfs_init_data_ref()`
- Queueing:
  - `btrfs_add_delayed_tree_ref()`
  - `btrfs_add_delayed_data_ref()`
  - `btrfs_add_delayed_extent_op()`
- Processing:
  - `btrfs_merge_delayed_refs()`
  - `btrfs_find_delayed_ref_head()`
  - `btrfs_delete_ref_head()`
  - `btrfs_select_ref_head()`
  - `btrfs_unselect_ref_head()`
  - `btrfs_select_delayed_ref()`
  - `btrfs_check_delayed_seq()`
  - `btrfs_find_delayed_tree_ref()`
- Reservation:
  - `btrfs_delayed_refs_rsv_release()`
  - `btrfs_update_delayed_refs_rsv()`
  - block-group insert/update reserve increment/decrement helpers
  - `btrfs_delayed_refs_rsv_refill()`
  - `btrfs_check_space_for_delayed_refs()`
- Cleanup:
  - `btrfs_put_delayed_ref()`
  - `btrfs_destroy_delayed_refs()`

Role in Btrfs:
This header is the delayed-ref contract for transaction and extent-tree code. It encodes how extent reference mutations are represented before they are applied to persistent extent metadata.
