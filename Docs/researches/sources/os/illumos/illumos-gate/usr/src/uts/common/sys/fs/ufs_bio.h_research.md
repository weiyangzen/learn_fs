# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_bio.h

## Role

Provides UFS buffer I/O statistics and kernel macros wrapping common buffer-cache helper routines.

## Key Interfaces

- `struct ufsbiostats` exposes kstat counters for UFS buffer reads, writes, fbiwrites, getpage misses/read-aheads, putpage sync/async writes, and pageio.
- Exports global `struct ufsbiostats ub`.
- Kernel prototypes:
  - `bread_common()`
  - `bwrite_common()`
  - `getblk_common()`

## Macros

- `UFS_BREAD()` calls `bread_common()`.
- `UFS_BWRITE()` writes and releases a buffer while clearing read/done/error/delayed-write flags.
- `UFS_BRWRITE()` marks `B_RETRYWRI` then writes like `UFS_BWRITE()`.
- `UFS_BWRITE2()` forces wait and does not release the buffer.
- `UFS_GETBLK()` calls `getblk_common()`.

## Risk Notes

These macros encode buffer lifetime and flag-clearing policy. Callers rely on whether buffers are released or retained, especially around metadata writeback and retry writes.
