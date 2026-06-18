## sources/test-tools/xfstests/tests/btrfs/012

Purpose: this conversion test verifies `btrfs-convert` from ext4 to btrfs, archived ext image integrity, rollback to ext4, and rollback failure after deleting the saved image subvolume.

Control flow: it requires scratch without automatic check, `btrfs-convert`, `mkfs.ext4`, `e2fsck`, `fssum`, non-zoned scratch, loop support, and ext4 kernel support. It creates an ext4 filesystem with test block size, mounts it manually, populates it with fsstress, records fssum, unmounts, converts to btrfs, mounts as btrfs, verifies original data, fscks the archived image, loop-mounts and verifies archived image contents, writes new btrfs data, rolls back, fscks and mounts restored ext4, verifies original data, converts again, deletes `ext2_saved`, and expects rollback to fail.

State and persistence: scratch changes filesystem type multiple times. Fssum baseline is stored in `$tmp.original`. A loop mount is created inside scratch at `mnt`.

Dependencies: `btrfs-convert`, ext4 tools, `mount`, `_run_fsstress`, `$FSSUM_PROG`, `_try_scratch_mount`, `$BTRFS_UTIL_PROG`, `_require_loop`, and `_require_extra_fs`.

Risks: conversion is destructive and incompatible with zoned devices. Block sizes larger than page size can make ext4 mount unsupported and produce notrun. SELinux mount options are disabled to avoid xattr mismatches. The final expected failure asserts return code exactly 1.

Test signals: fssum comparisons must pass, e2fsck must pass on archived/restored images, and final rollback after deleting `ext2_saved` must fail with code 1.
