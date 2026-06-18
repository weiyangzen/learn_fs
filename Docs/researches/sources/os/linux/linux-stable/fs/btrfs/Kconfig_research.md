# File Research: sources/os/linux/linux-stable/fs/btrfs/Kconfig

## Summary
Defines Btrfs kernel configuration options, dependencies, selected libraries, developer diagnostics, and experimental feature gating.

## Main Responsibilities
- Declares `BTRFS_FS` as tristate filesystem support.
- Selects compression, checksum, RAID, iomap, and block-cgroup dependencies.
- Defines optional POSIX ACL support.
- Defines module-load sanity tests.
- Defines debug and assertion options.
- Defines `BTRFS_EXPERIMENTAL` and documents experimental feature families.

## Important Behavior
`BTRFS_FS` depends on `PAGE_SIZE_LESS_THAN_256KB` and selects core implementation prerequisites such as CRC32, BLAKE2b, SHA256, zlib/lzo/zstd, RAID6/PQ, XOR, xxhash, and `FS_IOMAP`.

The experimental option gates unstable work including RAID read policy, send v3 fs-verity support, raid-stripe-tree, extent tree v2, large folios/block size, async checksums, and remap-tree.

## Risks
Kconfig selections encode build-time assumptions for the entire Btrfs module. Accidentally removing selects can produce missing symbols or disabled runtime features; enabling experimental features exposes users to intentionally unstable behavior.
