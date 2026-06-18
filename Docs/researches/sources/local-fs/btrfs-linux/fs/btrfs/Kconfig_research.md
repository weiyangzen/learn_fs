# File Research: sources/local-fs/btrfs-linux/fs/btrfs/Kconfig

Defines the kernel configuration surface for Btrfs.

Key points:
- `CONFIG_BTRFS_FS` is the main tristate module/built-in option.
- Main filesystem support selects checksum, compression, iomap, RAID parity, XOR, xxhash, and block-cgroup bio punt support.
- Depends on `PAGE_SIZE_LESS_THAN_256KB`, reflecting Btrfs metadata/page-size limits in this tree.
- `CONFIG_BTRFS_FS_POSIX_ACL` enables POSIX ACL support and selects `FS_POSIX_ACL`.
- `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` enables module-load regression/sanity tests.
- `CONFIG_BTRFS_DEBUG` enables runtime debugging, leak checks, debug sysfs, optional fragmentation behavior, and `REF_TRACKER` when stack traces are supported.
- `CONFIG_BTRFS_ASSERT` enables lightweight invariant assertions.
- `CONFIG_BTRFS_EXPERIMENTAL` gates unstable/developer-facing features, including raid-stripe-tree, extent tree v2, large folio/block size support, async checksum generation, remap-tree, send protocol v3 fs-verity support, and experimental read policy work.

Role in system:
- Establishes which Btrfs subsystems are compiled and which optional code paths are available.
- The config options directly drive `fs/btrfs/Makefile` object inclusion.
