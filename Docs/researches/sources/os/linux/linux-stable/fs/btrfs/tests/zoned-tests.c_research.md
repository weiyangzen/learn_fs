# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/zoned-tests.c

## Role

Self-tests for zoned-mode block-group allocation offset recovery across RAID profiles. The tests drive `btrfs_load_block_group_by_raid_type()` with synthetic zone write pointers, conventional zones, missing devices, degraded mode, and `last_alloc`.

## Main Entry Point

- `btrfs_test_zoned()`: allocates dummy `fs_info`, then runs every vector in `load_zone_info_tests`.

## Test Model

- `struct load_zone_info_test_vector`: describes RAID type, stripe count, per-stripe allocation offsets, last allocation, block group length, degraded flag, expected return, and expected recovered `alloc_offset`.
- `struct zone_info`: test-local physical/capacity/alloc-offset shape passed to production zoned loading code.
- Sentinel offsets:
  - `WP_MISSING_DEV`: missing stripe/device.
  - `WP_CONVENTIONAL`: conventional zone, where write pointer is not the same signal as sequential zones.
  - `ZONE_SIZE`: fixed 256 MiB synthetic zone capacity.

## Covered Profiles

- SINGLE: basic sequential write pointer recovery.
- DUP and RAID1: matching mirrors, sequential plus conventional zones, larger/smaller `last_alloc`, mismatched write pointers, missing devices, and degraded RAID1 recovery.
- RAID0: stripe-progress reconstruction, disordered stripes, far-distance errors, too many partial writes, missing device errors, and mixed sequential/conventional stripe cases.
- RAID10: mirror-pair equivalents of RAID0 cases, including sub-stripe setup and degraded/missing-device rejection for RAID0-level loss.

## Dependencies and Interactions

- Allocates dummy block groups with `btrfs_alloc_dummy_block_group()`.
- Allocates `btrfs_chunk_map` with the tested RAID profile and stripe count.
- Sets or clears `DEGRADED` mount option per vector.
- Uses cleanup attributes (`__free`, `AUTO_KFREE`) for local allocations.

## Error Handling Notes

- Some test vectors intentionally expect `-EIO`; the entry-point message notes error messages are expected.
- The test validates both return code and, for success, the recovered `bg->alloc_offset`.
