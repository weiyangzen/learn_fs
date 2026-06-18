# File Research: sources/os/linux/linux-stable/fs/btrfs/Makefile

## Summary
Builds the Btrfs module object list and conditionally includes optional ACL, debug, zoned, verity, and test objects.

## Main Responsibilities
- Adds Btrfs-specific warning flags.
- Builds `btrfs.o` for `CONFIG_BTRFS_FS`.
- Lists core Btrfs object files.
- Includes conditional objects for ACL, ref verification, zoned devices, fs-verity, and sanity tests.

## Important Behavior
The core object list wires together filesystem entry points, trees, transactions, inode/file I/O, extent maps, compression, delayed refs/inodes, scrub, backrefs, qgroups, send, device replace, RAID56, block groups, bio handling, direct I/O, and more.

Sanity tests are compiled only with `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, with zoned tests additionally gated by `CONFIG_BLK_DEV_ZONED`.

## Risks
Object ordering and conditional compilation define which subsystems are linked into the module. Missing `acl.o`, `zoned.o`, `verity.o`, or test objects under the wrong config would create feature or symbol mismatches.
