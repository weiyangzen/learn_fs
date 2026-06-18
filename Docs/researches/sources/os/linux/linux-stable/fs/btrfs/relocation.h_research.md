# File Research: sources/os/linux/linux-stable/fs/btrfs/relocation.h

This header declares the public relocation and remap-tree interface implemented in `relocation.c`.

Public API:
- `should_relocate_using_remap_tree()` selects remap-tree relocation when the filesystem has the `REMAP_TREE` incompat feature and the block group is not system or metadata-remap.
- `btrfs_relocate_block_group()` relocates all extents out of a block group.
- `btrfs_init_reloc_root()` and `btrfs_update_reloc_root()` manage relocation roots during transaction recording and commit.
- `btrfs_recover_relocation()` resumes or cleans interrupted relocation after a crash.
- `btrfs_reloc_clone_csums()` clones data checksums for ordered relocation writes.
- `btrfs_reloc_cow_block()` is the COW-time hook that tracks relocated tree blocks and updates file extent pointers.
- `btrfs_reloc_pre_snapshot()` and `btrfs_reloc_post_snapshot()` integrate relocation with snapshot creation.
- `btrfs_should_cancel_balance()` checks balance/relocation cancellation and fatal signals.
- `find_reloc_root()` looks up a reloc root by original root bytenr.
- `btrfs_should_ignore_reloc_root()` lets backref lookup ignore stale/dead reloc roots.
- `btrfs_get_reloc_bg_bytenr()` reports the currently relocating block group while relocation is active.
- `btrfs_translate_remap()` translates logical ranges through remap-tree items.
- `btrfs_remove_extent_from_remap_tree()` punches freed/allocated ranges out of remap-tree state.
- `btrfs_last_identity_remap_gone()` finishes removal of a chunk whose identity remaps are gone.

Dependencies and declarations:
- Includes `<linux/types.h>`.
- Forward declares Btrfs core types, ordered extents, pending snapshots, and extent buffers.
- The inline selector depends on `struct btrfs_block_group` fields and Btrfs incompat feature helpers available through surrounding Btrfs headers.

Role in the subsystem:
- Provides the narrow interface used by transaction, COW, snapshot, ordered extent, block-group, and remap-tree users without exposing relocation-control internals.
