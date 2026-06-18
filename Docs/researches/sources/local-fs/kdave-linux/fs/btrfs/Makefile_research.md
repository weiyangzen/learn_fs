# File Research: sources/local-fs/kdave-linux/fs/btrfs/Makefile

Purpose: Builds the Btrfs kernel module object list and applies Btrfs-local warning flags.

Build behavior:
- Adds a subset of `W=1` diagnostics: `-Wextra`, unused warnings, missing declarations/prototypes, old-style definition checks, missing include dirs, and compiler-supported optional warnings.
- Suppresses selected `-Wextra` warnings: missing field initializers, sign compare, and negative shift warnings.
- Builds `btrfs.o` when `CONFIG_BTRFS_FS` is enabled.
- Core object list includes tree, inode, transaction, extent, compression, relocation, qgroup, send, device replace, RAID56, free-space tree, tree checker, subpage, tree-mod-log, fs, bio, raid-stripe-tree, fiemap, direct I/O, and many more components.

Conditional objects:
- `acl.o` when `CONFIG_BTRFS_FS_POSIX_ACL`.
- `ref-verify.o` when `CONFIG_BTRFS_DEBUG`.
- `zoned.o` when `CONFIG_BLK_DEV_ZONED`.
- `verity.o` when `CONFIG_FS_VERITY`.
- Sanity test objects when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`; zoned tests are added only when zoned block device support is built in.

Integration notes: This file places the researched files in context: `accessors.o`, `async-thread.o`, `backref.o`, and `bio.o` are always part of `btrfs-y`; `acl.o` is config-gated.
