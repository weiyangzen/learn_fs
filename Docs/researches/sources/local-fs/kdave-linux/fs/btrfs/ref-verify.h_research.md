# File Research: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.h

## Purpose

`ref-verify.h` declares the debug reference verifier interface and provides no-op stubs when `CONFIG_BTRFS_DEBUG` is disabled.

## Debug Build Interface

When `CONFIG_BTRFS_DEBUG` is enabled, it declares:

- `btrfs_build_ref_tree()`: build verifier cache from the extent tree.
- `btrfs_free_ref_cache()`: free verifier state.
- `btrfs_ref_tree_mod()`: record/check one reference modification.
- `btrfs_free_ref_tree_range()`: remove verifier entries in a byte range.
- `btrfs_init_ref_verify()`: initialize the spinlock and block rb-tree.

`btrfs_init_ref_verify()` initializes:

- `fs_info->ref_verify_lock`
- `fs_info->block_tree = RB_ROOT`

## Non-Debug Build Behavior

When `CONFIG_BTRFS_DEBUG` is disabled, all functions are inline no-ops or return success. This removes verifier overhead from normal builds while allowing call sites to remain unconditional.

## Relationship

This header is the integration boundary between delayed-ref/extent-tree code and the verifier implementation in `ref-verify.c`.
