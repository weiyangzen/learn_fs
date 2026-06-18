# File Research: sources/local-fs/btrfs-linux/fs/btrfs/delayed-ref.h

This header defines the delayed ref structures, enums, inline helpers, and exported delayed ref API.

Key enums:
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

Key structures:
- `struct btrfs_data_ref`
  - Stores inode objectid and data offset identity for extent data refs.
- `struct btrfs_tree_ref`
  - Stores tree block level for metadata refs.
- `struct btrfs_delayed_ref_node`
  - Represents one queued add/drop ref.
  - Carries bytenr, length, sequence, ref root, parent, ref mod, action, type, and data/tree identity.
- `struct btrfs_delayed_extent_op`
  - Holds delayed extent item key/flag updates.
- `struct btrfs_delayed_ref_head`
  - Represents all queued operations for one extent.
  - Holds mutex, ref tree, add list, extent op, total/current ref mods, owning root, reserved bytes, level, and processing/tracking flags.
- `struct btrfs_delayed_ref_root`
  - Tracks head refs and dirty qgroup extent records in xarrays.
  - Maintains counts, pending checksum bytes, flags, run cursor, and qgroup skip root.
- `struct btrfs_ref`
  - Generic input descriptor used to create delayed data or metadata refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` estimates metadata reservation for delayed refs, doubling when free-space-tree updates are required.
- `btrfs_calc_delayed_ref_csum_bytes()` estimates csum deletion metadata.
- `btrfs_alloc_delayed_extent_op()` / `btrfs_free_delayed_extent_op()` manage extent op slab objects.
- `btrfs_ref_head_to_space_flags()` maps a head to data/system/metadata block group flags.
- `btrfs_put_delayed_ref_head()` releases head refs.
- `btrfs_delayed_ref_unlock()` unlocks a selected head.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose type-dependent identity fields.
- `btrfs_ref_type()` maps generic ref fields to Btrfs backref item key type.

Exported API:
- Slab lifecycle: `btrfs_delayed_ref_init()`, `btrfs_delayed_ref_exit()`.
- Generic ref initialization: `btrfs_init_tree_ref()`, `btrfs_init_data_ref()`.
- Queueing: `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, `btrfs_add_delayed_extent_op()`.
- Selection/lookup: `btrfs_find_delayed_ref_head()`, `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_find_delayed_tree_ref()`.
- Reservation accounting: delayed refs reserve release/update/refill and block-group insert/update helpers.
- Cleanup: `btrfs_delete_ref_head()`, `btrfs_destroy_delayed_refs()`.
