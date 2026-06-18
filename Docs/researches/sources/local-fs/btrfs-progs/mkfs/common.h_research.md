# File Research: sources/local-fs/btrfs-progs/mkfs/common.h

## Purpose
Public mkfs common API and configuration definitions.

## Key Contents
- Defines initial mkfs constants: `BTRFS_MKFS_SYSTEM_GROUP_SIZE`, `BTRFS_MKFS_SMALL_VOLUME_SIZE`, and default one-device/multi-device data/metadata profiles.
- Defines `enum btrfs_mkfs_block` for initial tree blocks and `MKFS_BLOCK_COUNT`.
- Defines `default_blocks[]` with the default initial tree block set.
- Defines `struct btrfs_mkfs_config`, including input settings, feature flags, sizes, checksumming, zone size, output block addresses, UUID strings, and superblock offset.
- Declares `make_btrfs()`, minimum-size/profile validation helpers, and target-device status checks.

## Dependencies
Includes `kerncompat.h`, `<stdbool.h>`, `kernel-lib/sizes.h`, btrfs UAPI constants, common definitions, and fs feature types.

## Risks
- `default_blocks[]` is a `static const` array in a header, so each translation unit gets its own copy. That is acceptable for a small constant table but should remain intentional.
- `cfg->blocks` is sized as `MKFS_BLOCK_COUNT + 1`, while enum values are currently below `MKFS_BLOCK_COUNT`; the extra slot is unused defensive space.
