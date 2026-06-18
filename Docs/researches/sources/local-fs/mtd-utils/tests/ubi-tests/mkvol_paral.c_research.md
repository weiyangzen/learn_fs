# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_paral.c

## Role
Parallel create/delete stress test for UBI volumes.

## Main Behavior
- Starts four pthreads.
- Each thread repeatedly creates an automatically numbered dynamic volume, then immediately removes it.
- Uses small volume size `dev_info.avail_bytes / ITERATIONS`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses pthreads and shared `libubi` descriptor.

## Notes
- Threads do not report a failure flag to `main()`; failures are logged but final exit can still be success after thread join.
- Exercises kernel/libubi synchronization around volume ID allocation and removal.
