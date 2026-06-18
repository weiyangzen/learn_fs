# sources/test-tools/kdevops/workflows/fio-tests/sections.conf

## Purpose
INI-style manifest of filesystem configurations for fio-tests multi-filesystem runs.

## Important APIs, Types, and Functions
Sections include XFS 4K/16K/32K/64K, `xfs-all-block-sizes`, ext4 standard/bigalloc, and btrfs standard/zstd. Most sections define `filesystem`, `mkfs_opts`, and `mount_opts`.

## Control Flow
No executable control flow. Consumers parse sections to create and mount filesystems before fio runs.

## State and Persistence Behavior
Static configuration only. Runtime filesystem and mount state is produced by consumers.

## Dependencies and Integration Points
Integrates with fio-tests roles and Kconfig variants. Requires mkfs tools that support listed flags.

## Risks and Edge Cases
`[xfs-all-block-sizes]` has no key/value settings and needs consumer special handling. Large XFS blocks, ext4 bigalloc, and btrfs zstd require compatible kernel/tool support.

## Test Signals
Parse with the intended config parser, verify Kconfig-to-section mapping, and run mkfs/mount smoke tests on disposable devices.
