# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.h

This header declares the Btrfs reference-verification hooks and hides them behind `CONFIG_BTRFS_DEBUG`.

Debug build interface:
- Includes `spinlock.h` because `btrfs_init_ref_verify()` initializes `fs_info->ref_verify_lock`.
- Declares `btrfs_build_ref_tree()` for mount-time extent-tree scanning.
- Declares `btrfs_free_ref_cache()` for unmount/failure cleanup.
- Declares `btrfs_ref_tree_mod()` for delayed-ref add/drop verification.
- Declares `btrfs_free_ref_tree_range()` for removing verifier state over a block-group range.
- `btrfs_init_ref_verify()` initializes the verifier spinlock and sets `fs_info->block_tree = RB_ROOT`.

Non-debug build behavior:
- All hooks are static inline no-ops or return 0.
- This lets common mount, unmount, block-group, and extent-tree code call verifier functions unconditionally without scattering `#ifdef CONFIG_BTRFS_DEBUG`.

Cross-file relationships:
- `disk-io.c` calls init/build/free lifecycle hooks.
- `extent-tree.c` calls `btrfs_ref_tree_mod()`.
- `block-group.c` calls `btrfs_free_ref_tree_range()`.
- `super.c` manages the runtime `REF_VERIFY` option, but the header determines whether the implementation exists.

Important invariants:
- `struct btrfs_fs_info` and `struct btrfs_ref` are forward-declared so this header does not pull in the full extent-tree internals.
- The runtime `REF_VERIFY` mount option only has operational effect when `CONFIG_BTRFS_DEBUG` is enabled.
