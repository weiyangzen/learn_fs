# File Research: sources/os/linux/linux-stable/fs/btrfs/ref-verify.h

## Purpose

Declares the Btrfs reference verifier interface and provides no-op stubs when debug support is disabled.

## Debug Build Behavior

Under `CONFIG_BTRFS_DEBUG`, it declares:

- `btrfs_build_ref_tree()`
- `btrfs_free_ref_cache()`
- `btrfs_ref_tree_mod()`
- `btrfs_free_ref_tree_range()`

It also defines `btrfs_init_ref_verify()`, which initializes `fs_info->ref_verify_lock` and sets `fs_info->block_tree` to `RB_ROOT`.

## Non-Debug Build Behavior

Without `CONFIG_BTRFS_DEBUG`, all functions are inline no-ops or return success. This removes verifier overhead entirely from non-debug builds while preserving call-site simplicity.

## Role in the Subsystem

This header gates the verifier behind debug configuration and mount-option checks. Production code can call the verifier hooks unconditionally while compilation determines whether they do real work.
