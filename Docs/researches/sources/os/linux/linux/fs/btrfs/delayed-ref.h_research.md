# File Research: sources/os/linux/linux/fs/btrfs/delayed-ref.h

This header defines delayed back reference data structures, reservation helpers, and the public delayed-ref API.

Key types:
- `enum btrfs_delayed_ref_action` defines add, drop, new extent allocation, and head update actions.
- `struct btrfs_data_ref` stores the inode objectid and adjusted file offset for data extent refs.
- `struct btrfs_tree_ref` stores tree block level for metadata refs.
- `struct btrfs_delayed_ref_node` is one queued reference operation, with rb/list links, bytenr, size, sequence, root/parent identity, refcount, ref modification count, action, ref item type, and data/tree ref payload.
- `struct btrfs_delayed_extent_op` stores delayed extent item key/flag updates.
- `struct btrfs_delayed_ref_head` aggregates all pending changes for one extent, owns a lock, rbtree, add list, extent op, ref modification counters, reservation state, block group type flags, and processing/tracking booleans.
- `struct btrfs_delayed_ref_root` stores transaction-wide head and qgroup dirty extent xarrays, counters, pending csum bytes, run cursor, flags, and qgroup skip root.
- `struct btrfs_ref` is the generic input representation used to queue data or metadata delayed refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` estimates metadata reservation for delayed refs and doubles it when the free space tree is active.
- `btrfs_calc_delayed_ref_csum_bytes()` estimates metadata needed to delete checksum items.
- `btrfs_alloc_delayed_extent_op()` and `btrfs_free_delayed_extent_op()` wrap the extent op slab cache.
- `btrfs_put_delayed_ref_head()` and `btrfs_put_delayed_ref()` handle refcounted delayed ref object release.
- `btrfs_ref_head_to_space_flags()` maps a delayed ref head to data, system, or metadata block group flags.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose owner/offset interpretation based on ref item type.
- `btrfs_ref_type()` maps generic data/metadata refs with or without parent pointers to the correct on-disk ref item type.

Exported API:
- Slab lifecycle: `btrfs_delayed_ref_init()` and `btrfs_delayed_ref_exit()`.
- Generic ref initialization: `btrfs_init_tree_ref()` and `btrfs_init_data_ref()`.
- Queueing: `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, and `btrfs_add_delayed_extent_op()`.
- Merge/select/run support: `btrfs_merge_delayed_refs()`, `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_delete_ref_head()`, and `btrfs_find_delayed_ref_head()`.
- Reservation management: `btrfs_delayed_refs_rsv_release()`, `btrfs_update_delayed_refs_rsv()`, block group insert/update accounting helpers, `btrfs_delayed_refs_rsv_refill()`, and `btrfs_check_space_for_delayed_refs()`.
- Lookup/cleanup: `btrfs_find_delayed_tree_ref()` and `btrfs_destroy_delayed_refs()`.
