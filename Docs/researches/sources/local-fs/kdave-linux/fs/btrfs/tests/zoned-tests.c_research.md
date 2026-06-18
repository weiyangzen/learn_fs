# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/zoned-tests.c

## Purpose

This file implements Btrfs zoned-mode selftests for loading a block group allocation offset from per-zone write pointer state. It checks `btrfs_load_block_group_by_raid_type()` across SINGLE, DUP, RAID1, RAID0, and RAID10 layouts, including mixed sequential/conventional zones and degraded/missing-device cases.

## Main Entry Point

- `btrfs_test_zoned(void)`: allocates a dummy `fs_info`, iterates `load_zone_info_tests[]`, and runs `test_load_zone_info()` for each vector.

## Test Data Model

`struct load_zone_info_test_vector` describes each case:
- `raid_type`: Btrfs block group profile.
- `num_stripes`: stripe count.
- `alloc_offsets[8]`: per-stripe zone allocation/write pointer state.
- `last_alloc`: last known allocation offset for conventional-zone reconstruction.
- `bg_length`: block group length passed to dummy block group allocator.
- `degraded`: whether mount option `DEGRADED` should be set.
- `expected_result`: expected return value, default zero.
- `expected_alloc_offset`: expected `bg->alloc_offset` on success.
- `description`: failure context.

Special sentinel offsets:
- `WP_MISSING_DEV`: missing stripe/device.
- `WP_CONVENTIONAL`: conventional zone.
- Normal numeric values represent sequential-zone write pointer offsets.

`struct zone_info` supplies the minimal per-stripe physical/capacity/alloc-offset shape consumed by the target zoned code.

## Harness Behavior

`test_load_zone_info()`:
- Allocates a dummy block group and chunk map.
- Allocates `zone_info` and an active-zone bitmap.
- Sets map type, stripe count, and RAID10 sub-stripes when needed.
- Initializes each zone with capacity `ZONE_SIZE` and vector-provided offset.
- Marks a stripe active if its offset is nonzero and inside the zone.
- Toggles `DEGRADED` mount option according to the vector.
- Calls `btrfs_load_block_group_by_raid_type()`.
- Verifies both return code and successful `bg->alloc_offset`.

## Covered Cases

The vector table covers:

- SINGLE:
  - Sequential zone write pointer load.

- DUP and RAID1:
  - Matching write pointers.
  - Sequential plus conventional zone with matching `last_alloc`.
  - Sequential plus conventional zone with smaller `last_alloc`, accepting the sequential write pointer.
  - Different write pointers as `-EIO`.
  - Missing device behavior, with RAID1 degraded recovery expected to succeed.
  - Conventional/sequence combinations where `last_alloc` is larger than allowed as `-EIO`.

- RAID0:
  - Initial partial write.
  - Progress through second stripe.
  - One stripe advanced.
  - Disordered stripe progression.
  - Excess distance between stripes.
  - Too many partial writes.
  - Missing device under degraded mount still rejected.
  - Sequential/conventional combinations where `last_alloc` reconstructs the global allocation pointer.
  - Four-stripe mixed conventional cases with expected reconstructed offsets and failure for inconsistent `last_alloc`.

- RAID10:
  - Same style as RAID0, but with mirrored sub-stripe pairs.
  - Matching mirrored pair progression.
  - Conventional-zone combinations.
  - Disordered/far/too-many-partial failures.
  - Missing mirror group under degraded mount rejected for RAID0-level loss semantics.
  - Eight-stripe mixed conventional reconstruction cases.

## Dependencies and Integration

This selftest depends on:
- Dummy fs/block group helpers from the Btrfs selftest framework.
- Chunk map allocation/freeing from `volumes.h`.
- Zoned allocator logic from `zoned.h`.
- Linux cleanup attributes and allocation helpers.

It tests the zoned block-group load logic without real zoned devices by supplying synthetic per-zone metadata.

## Important Invariants

- `ZONE_SIZE` is fixed at 256 MiB.
- Stripe progression is evaluated in units of `BTRFS_STRIPE_LEN`; `HALF_STRIPE_LEN` is used for partial-stripe cases.
- Active bitmap bits are set only for sequential zones with an in-zone nonzero allocation offset.
- `bg->alloc_offset` is checked only when the target function succeeds.
- Expected error messages are normal because invalid vectors deliberately exercise corruption/inconsistency detection.

## Error Handling

Allocation failures return `-ENOMEM`. Unexpected target return values or allocation offsets return `-EINVAL` after a `test_err()` diagnostic.

## Research Notes

The test table is the core of this file. It documents zoned write-pointer reconstruction rules for mirrored, striped, and mixed conventional/sequential layouts in executable form.
