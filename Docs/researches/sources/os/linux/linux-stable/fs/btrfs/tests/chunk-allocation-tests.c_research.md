# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/chunk-allocation-tests.c

## Role
Unit tests the pending extent internals used by Btrfs chunk allocation. The tested behavior is limited and precise: finding the first pending allocation in a range and finding a usable hole after excluding pending allocations.

## Main Tests
- `find_hole_tests` describes input search ranges, required minimum hole sizes, up to two pending extents, and expected hole discovery results for `btrfs_find_hole_in_pending_extents`.
- `test_find_hole_in_pending` allocates dummy fs_info/device state, marks pending extents with `CHUNK_ALLOCATED` in the device allocation state tree, calls the function under `chunk_mutex`, validates found/start/length outputs, and clears pending state between cases.
- `first_pending_tests` describes ranges and a single pending extent for `btrfs_first_pending_extent`.
- `test_first_pending_extent` validates no-pending, pending-at-start, overlap-at-start, inside-range, outside-range, and overlap-at-end cases.
- `btrfs_test_chunk_allocation` runs first-pending tests followed by find-hole tests.

## Coverage Notes
The test vectors cover empty ranges, zero-length input, pending allocations at boundaries, overlaps with the searched range, three-hole selection, holes smaller than the requested minimum, and reporting of the largest insufficient hole when no acceptable hole exists.

## Dependencies
Depends on the common Btrfs self-test harness, dummy devices, volume allocation-state trees, disk I/O initialization, and extent I/O tree bit operations.
