# File Research: sources/os/linux/linux/fs/btrfs/Kconfig

Purpose: Defines the kernel configuration surface for Btrfs.

Key options:
- `BTRFS_FS`: main tristate filesystem option. Selects block cgroup bio punting, CRC/checksum libraries, compression libraries, iomap, RAID6/XOR helpers, and xxhash. Depends on `PAGE_SIZE_LESS_THAN_256KB`.
- `BTRFS_FS_POSIX_ACL`: enables POSIX ACL support through `FS_POSIX_ACL`.
- `BTRFS_FS_RUN_SANITY_TESTS`: runs Btrfs regression/sanity tests at module load.
- `BTRFS_DEBUG`: enables expensive debugging checks, leak checks, extra sysfs debug output, forced fragmentation, and `REF_TRACKER` when stack traces are supported.
- `BTRFS_ASSERT`: enables runtime invariant assertions that may panic on violation.
- `BTRFS_EXPERIMENTAL`: gates unstable features, including COW fixup warning, mirror read policies, send stream v3 fs-verity, raid-stripe-tree, extent tree v2, large folio/block-size support, async data-write checksumming, and remap-tree.

Integration: These options directly control objects and code paths in the Btrfs Makefile and implementation files, including ACL support, debug-only ref verification, sanity tests, and experimental async checksum behavior in `bio.c`.

Risk notes: `BTRFS_EXPERIMENTAL` enables several unrelated unstable features at once, and `BTRFS_ASSERT` can intentionally panic on invariant failure.
