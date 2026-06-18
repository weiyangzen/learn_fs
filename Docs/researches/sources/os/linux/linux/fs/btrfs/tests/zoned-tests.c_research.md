# File Research: sources/os/linux/linux/fs/btrfs/tests/zoned-tests.c

## Purpose

This file implements Btrfs zoned-mode selftests for loading a block group allocation offset from per-zone write pointer state. It validates `btrfs_load_block_group_by_raid_type()` across SINGLE, DUP, RAID1, RAID0, and RAID10 layouts.

## Main Entry Point

- `btrfs_test_zoned(void)`: allocates dummy `fs_info`, iterates `load_zone_info_tests[]`, and runs `test_load_zone_info()` for each vector.

## Test Data Model

`struct load_zone_info_test_vector` defines:
- `raid_type`: Btrfs block group profile.
- `num_stripes`: number of stripes in the synthetic chunk map.
- `alloc_offsets[8]`: per-stripe write pointer or sentinel.
- `last_alloc`: prior allocation offset used when conventional zones are involved.
- `bg_length`: dummy block group length.
- `degraded`: whether mount option `DEGRADED` is set.
- `expected_result`: expected return value.
- `expected_alloc_offset`: expected `bg->alloc_offset` on success.
- `description`: test label.

Special sentinel values:
- `WP_MISSING_DEV`: missing device/stripe.
- `WP_CONVENTIONAL`: conventional zone.
- Numeric values represent sequential-zone write pointer offsets.

`struct zone_info` is the minimal shape needed by the target zoned code: physical, capacity, and allocation offset.

## Harness Behavior

`test_load_zone_info()`:
- Allocates a dummy block group and chunk map.
- Allocates zone info and an active-zone bitmap.
- Sets `map->type`, `map->num_stripes`, and RAID10 `sub_stripes`.
- Fills each synthetic zone with capacity `ZONE_SIZE`.
- Marks a zone active if its allocation offset is nonzero and inside the zone.
- Toggles `DEGRADED` mount option from the vector.
- Calls `btrfs_load_block_group_by_raid_type()`.
- Verifies both return code and successful `bg->alloc_offset`.

## Covered Cases

SINGLE:
- Sequential zone write pointer loading.

DUP and RAID1:
- Matching write pointers.
- Sequential plus conventional zone with matching `last_alloc`.
- Sequential plus conventional zone with smaller `last_alloc`.
- Different write pointers as `-EIO`.
- Missing-device cases, including degraded RAID1 recovery.
- Sequential/conventional combinations with too-large `last_alloc` as `-EIO`.

RAID0:
- Initial partial write.
- Progression into later stripes.
- One stripe advanced.
- Disordered stripe progression.
- Excessive distance between stripes.
- Too many partial writes.
- Missing device under degraded mount rejected.
- Sequential/conventional reconstruction from `last_alloc`.
- Four-stripe mixed conventional cases with success and failure expectations.

RAID10:
- RAID0-like progression across mirrored stripe pairs.
- Mirrored pair consistency.
- Conventional-zone combinations.
- Disordered, far-distance, too-many-partial, and missing mirror-group failures.
- Eight-stripe mixed conventional reconstruction cases.

## Key Dependencies

- Dummy fs/block group helpers.
- Chunk map allocation/freeing from `volumes.h`.
- Zoned allocator logic from `zoned.h`.
- Linux cleanup attributes and bitmap helpers.

## Important Invariants

- RAID10 test vectors set `map->sub_stripes = 2`.
- Active-zone state is derived from nonzero write pointers below `ZONE_SIZE`.
- Missing devices and conventional zones are represented as high sentinel `u64` values.
- Expected failures are part of normal test coverage; the entry point logs that error messages are expected.

## Research Notes

The test is vector-driven and compact. One notable implementation detail: after `bitmap_zalloc()`, the failure check tests `zone_info` again instead of `active`; if bitmap allocation failed, the current code would not catch it at that branch.
