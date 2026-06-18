# File Research: sources/os/linux/linux/fs/btrfs/ref-verify.h

## Scope

`ref-verify.h` declares the reference verifier interface and provides debug/non-debug build variants.

## APIs

When `CONFIG_BTRFS_DEBUG` is enabled:

- `btrfs_build_ref_tree()`
- `btrfs_free_ref_cache()`
- `btrfs_ref_tree_mod()`
- `btrfs_free_ref_tree_range()`
- `btrfs_init_ref_verify()`

`btrfs_init_ref_verify()` initializes `fs_info->ref_verify_lock` and sets `fs_info->block_tree` to `RB_ROOT`.

When debug support is disabled, all functions are inline no-ops returning success where needed.

## Dependencies

The debug path uses Linux spinlocks and rbtrees plus forward declarations of `btrfs_fs_info` and `btrfs_ref`.

## Risks And Invariants

Callers can invoke these APIs unconditionally because the header compiles them out in non-debug builds. Debug builds require `btrfs_init_ref_verify()` before verifier tree use.
