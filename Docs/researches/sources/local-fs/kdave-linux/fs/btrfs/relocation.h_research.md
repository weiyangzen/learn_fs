# File Research: sources/local-fs/kdave-linux/fs/btrfs/relocation.h

## Purpose

`relocation.h` declares the public Btrfs relocation interface used by balance, resize, transaction, snapshot, remap-tree, ordered-extent, and COW paths.

## Exposed Policy Helper

`should_relocate_using_remap_tree()` returns true only when:

- the filesystem has the `REMAP_TREE` incompat feature;
- the block group is not system metadata;
- the block group is not marked `BTRFS_BLOCK_GROUP_METADATA_REMAP`.

This keeps remap-tree relocation out of system chunks and metadata-remap chunks while allowing eligible data and metadata block groups to use the newer remap path.

## Declared APIs

- `btrfs_relocate_block_group()`: relocate all extents out of a block group.
- `btrfs_init_reloc_root()` / `btrfs_update_reloc_root()`: transaction-time reloc-root lifecycle hooks.
- `btrfs_recover_relocation()`: recover interrupted relocations at mount time.
- `btrfs_reloc_clone_csums()`: clone checksums for relocation ordered extents.
- `btrfs_reloc_cow_block()`: COW hook for relocation bookkeeping and data-pointer replacement.
- `btrfs_reloc_pre_snapshot()` / `btrfs_reloc_post_snapshot()`: snapshot integration hooks.
- `btrfs_should_cancel_balance()`: balance/relocation cancellation check.
- `find_reloc_root()`: lookup reloc root by original tree root bytenr.
- `btrfs_should_ignore_reloc_root()`: backref lookup helper for stale/dead reloc roots.
- `btrfs_get_reloc_bg_bytenr()`: report currently relocating block group.
- `btrfs_translate_remap()`: translate a logical range through remap-tree items.
- `btrfs_remove_extent_from_remap_tree()`: remove a freed range from remap-tree coverage.
- `btrfs_last_identity_remap_gone()`: finalize chunk/block-group metadata after the last identity remap disappears.

## Dependencies And Integration

The header forward-declares Btrfs core types and includes only `<linux/types.h>`, making it a low-overhead interface header. It depends on `struct btrfs_block_group` being visible to callers using the inline helper, so including files must already have the block-group definition available.

## Risk Notes

The inline helper encodes an important feature-policy gate. Any caller bypassing it could accidentally use remap-tree relocation for block groups that must stay on the classic path, especially system or metadata-remap groups.
