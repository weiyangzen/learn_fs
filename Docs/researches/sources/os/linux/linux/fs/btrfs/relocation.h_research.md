# File Research: sources/os/linux/linux/fs/btrfs/relocation.h

## Purpose

This header declares the public Btrfs relocation interface used by transaction, root, snapshot, checksum, block group, and remap-tree code.

## Exposed Policy

- `should_relocate_using_remap_tree()` selects the remap-tree relocation path only when:
  - the filesystem has the `REMAP_TREE` incompat feature
  - the block group is not a system block group
  - the block group is not a metadata-remap block group

This inline helper keeps relocation-mode selection shared and explicit.

## Declared APIs

Classic relocation:
- `btrfs_relocate_block_group()`
- `btrfs_recover_relocation()`
- `btrfs_should_cancel_balance()`
- `btrfs_get_reloc_bg_bytenr()`

Relocation root lifecycle:
- `btrfs_init_reloc_root()`
- `btrfs_update_reloc_root()`
- `find_reloc_root()`
- `btrfs_should_ignore_reloc_root()`

CoW/checksum/snapshot hooks:
- `btrfs_reloc_cow_block()`
- `btrfs_reloc_clone_csums()`
- `btrfs_reloc_pre_snapshot()`
- `btrfs_reloc_post_snapshot()`

Remap-tree support:
- `btrfs_translate_remap()`
- `btrfs_remove_extent_from_remap_tree()`
- `btrfs_last_identity_remap_gone()`

## Integration Role

The header lets other Btrfs subsystems call into relocation without exposing `struct reloc_control`. That keeps most relocation state private to `relocation.c` while still wiring relocation into transaction COW, ordered extents, snapshot creation, logical address translation, and chunk cleanup.

## Risk Notes

The inline remap-tree eligibility helper is small but important: routing system or metadata-remap block groups into remap relocation would be unsafe. Callers must also obey locking assumptions documented in the implementation, especially for `btrfs_get_reloc_bg_bytenr()` which expects `reloc_mutex` to be held.
