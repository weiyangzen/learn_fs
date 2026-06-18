# File Research: sources/local-fs/btrfs-linux/fs/btrfs/Makefile

Build recipe for the Btrfs kernel module/object.

Key points:
- Adds a selected subset of `W=1` compiler warnings for the whole Btrfs subdirectory.
- Main target is `obj-$(CONFIG_BTRFS_FS) := btrfs.o`.
- Core `btrfs-y` object list includes metadata trees, inode/file paths, extent I/O, volumes, compression, delayed refs/inodes, relocation, scrub, backrefs, qgroups, send, RAID56, free-space tree, block groups, discard, reflink, subpage, tree-mod-log, messages, bio, fiemap, direct I/O, and raid-stripe-tree.
- Conditional objects:
  - `acl.o` for `CONFIG_BTRFS_FS_POSIX_ACL`.
  - `ref-verify.o` for `CONFIG_BTRFS_DEBUG`.
  - `zoned.o` for `CONFIG_BLK_DEV_ZONED`.
  - `verity.o` for `CONFIG_FS_VERITY`.
- Sanity test objects are compiled under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.
- Zoned tests are only included when both sanity tests and zoned block device support are enabled.

Role in system:
- Connects feature flags from `Kconfig` to concrete compilation units.
- The file also shows the broad subsystem boundaries of Btrfs in this source tree.
