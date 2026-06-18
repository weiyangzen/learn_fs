# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/zoned-tests.c

## Summary
Selftests zoned block-group write-pointer loading for different RAID profiles, conventional/sequential zone mixtures, degraded cases, and invalid write-pointer patterns.

## Main Responsibilities
- Define table-driven test vectors for `btrfs_load_block_group_by_raid_type()`.
- Model per-stripe physical address, capacity, and allocation offset.
- Mark active stripes when sequential-zone write pointers are nonzero and within zone capacity.
- Toggle the dummy filesystem `DEGRADED` mount option per case.
- Verify expected return code and computed `bg->alloc_offset`.

## Key APIs
- Test entry: `btrfs_test_zoned()`.
- Harness: `test_load_zone_info()`.
- Data structures: `load_zone_info_test_vector`, local `zone_info`.
- API under test: `btrfs_load_block_group_by_raid_type()`.

## Important Behavior
The vector table covers SINGLE, DUP, RAID1, RAID0, and RAID10.

DUP and RAID1 validate matching mirrored write pointers, sequential plus conventional-zone handling via `last_alloc`, erroring on mismatched write pointers, and missing-device behavior. RAID1 accepts a partial missing device only for degraded mount; DUP treats partial missing device as invalid.

RAID0 and RAID10 validate stripe-progress reconstruction across partially written stripes, one-stripe-advanced cases, conventional-zone gaps, and `last_alloc` reconciliation. They reject disordered stripes, excessive distance between write pointers, too many partial writes, and missing stripes in RAID0-level layouts even when degraded.

The test uses sentinel values `WP_MISSING_DEV` and `WP_CONVENTIONAL` to describe unavailable or conventional-zone stripes.

## Setup and State
Each test allocates a dummy block group and chunk map, fills per-stripe test zone info, sets RAID10 `sub_stripes = 2`, and passes an active bitmap to the zoned loader.

## Risks
The table encodes expected allocator reconstruction semantics. Changes to zoned RAID placement, conventional-zone treatment, or degraded acceptance rules must update both the vector descriptions and expected offsets/errors.
