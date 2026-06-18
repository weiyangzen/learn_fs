# File Research: sources/os/linux/linux/fs/btrfs/Makefile

Purpose: Builds the Btrfs kernel module and applies Btrfs-local compiler warning flags.

Build behavior:
- Adds a subset of `W=1` diagnostics such as `-Wextra`, unused warnings, missing declarations/prototypes, missing format attributes, old-style definitions, and missing include dirs.
- Adds compiler-supported optional diagnostics for unused-but-set variables, unused const variables, packed alignment, string truncation, and maybe-uninitialized.
- Suppresses selected `-Wextra` warnings for missing field initializers, sign comparisons, and negative shifts.
- Builds `btrfs.o` when `CONFIG_BTRFS_FS` is enabled.

Core object list: Includes superblock, trees, extents, items, disk I/O, transactions, inode/file paths, extent maps, sysfs, accessors, xattrs, ordered data, volumes, async workers, ioctl, locking, orphan handling, export, tree-log, free-space cache/tree, compression backends, delayed refs/inodes, scrub, backrefs, qgroups, send, device replace, RAID56, UUID tree, props, tree checker, space info, block reservations, block groups, discard, reflink, subpage, tree-mod-log, fs support, messages, bio, raid-stripe-tree, fiemap, and direct I/O.

Conditional objects:
- `acl.o` under `CONFIG_BTRFS_FS_POSIX_ACL`.
- `ref-verify.o` under `CONFIG_BTRFS_DEBUG`.
- `zoned.o` under `CONFIG_BLK_DEV_ZONED`.
- `verity.o` under `CONFIG_FS_VERITY`.
- Sanity test objects under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, with zoned tests only when zoned block device support is enabled.

Integration notes: In this work item, `accessors.o`, `async-thread.o`, `backref.o`, and `bio.o` are core Btrfs objects; `acl.o` is config-gated.
