# File Research: sources/local-fs/btrfs-linux/fs/btrfs/relocation.h

This header declares the Btrfs relocation interface used by balance, transaction commit, COW, snapshot, inode writeback, extent-freeing, and volume mapping code.

Public helper:
- `should_relocate_using_remap_tree()` returns true only when the filesystem has the `REMAP_TREE` incompat feature and the block group is not system and not `BTRFS_BLOCK_GROUP_METADATA_REMAP`.

Declared relocation APIs:
- `btrfs_relocate_block_group()` relocates all extents in a block group.
- `btrfs_init_reloc_root()` and `btrfs_update_reloc_root()` create/update relocation roots during transactions.
- `btrfs_recover_relocation()` resumes interrupted relocation on mount.
- `btrfs_reloc_clone_csums()` attaches cloned checksum records to relocated ordered extents.
- `btrfs_reloc_cow_block()` lets COW code notify relocation about newly COWed tree blocks.
- `btrfs_reloc_pre_snapshot()` and `btrfs_reloc_post_snapshot()` adjust snapshot reservations and create relocation roots for snapshots created during relocation.
- `btrfs_should_cancel_balance()` exposes the relocation/balance cancellation predicate.
- `find_reloc_root()` looks up a relocation root by the source root block bytenr.
- `btrfs_should_ignore_reloc_root()` tells backref lookup when an old relocation root should be ignored.
- `btrfs_get_reloc_bg_bytenr()` reports the currently relocating block group start while holding `reloc_mutex`.
- `btrfs_translate_remap()` maps logical addresses through the remap tree.
- `btrfs_remove_extent_from_remap_tree()` removes freed ranges from remap-tree records.
- `btrfs_last_identity_remap_gone()` performs final chunk/block-group cleanup after the last identity remap disappears.

Integration notes:
- The header forward-declares the heavy Btrfs structures but relies on callers already having definitions for `struct btrfs_block_group`, `struct btrfs_path`, and `struct btrfs_chunk_map` through surrounding includes.
- The remap-tree APIs are coupled to volume mapping, extent freeing, block-group cleanup, and chunk/device extent maintenance.
