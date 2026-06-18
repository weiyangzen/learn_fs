# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fastio.c

Purpose: Defines VFAT Fast I/O dispatch callbacks and cache-manager acquire/release callbacks.

Key routines:
- `VfatFastIoCheckIfPossible`, `VfatFastIoRead`, `VfatFastIoWrite`, file-lock callbacks, MDL callbacks, compressed I/O callbacks, device control, query-open, and network-open callbacks return `FALSE` or `STATUS_INVALID_DEVICE_REQUEST`, preventing those fast paths.
- `VfatFastIoQueryBasicInfo` and `VfatFastIoQueryStandardInfo` acquire the FCB shared resource and delegate to `VfatGetBasicInformation` / `VfatGetStandardInformation`.
- `VfatAcquireForCcFlush` and `VfatReleaseForCcFlush` acquire/release the FCB main resource for cache flushes.
- `VfatAcquireForLazyWrite` and `VfatReleaseFromLazyWrite` provide cache-manager lazy-writer synchronization around `MainResource`.
- `VfatInitFastIoRoutines` fills the `FAST_IO_DISPATCH` table.

Implementation notes:
- The driver deliberately disables data Fast I/O by returning `FALSE`, which forces normal IRP paths for reads, writes, locks, MDL I/O, compressed I/O, and query-open.
- Fast basic/standard information queries are supported only when the FCB can be locked without violating the caller's `Wait` parameter.
- Page-file FCBs bypass normal resource locking in the query-info fast paths.

Dependencies and interactions:
- Uses `VfatGetBasicInformation` and `VfatGetStandardInformation` from `finfo.c`.
- The cache manager uses lazy-write and flush acquire/release callbacks for synchronization with cached file data.

Notable limitations:
- Section create acquire/release callbacks are no-ops, and most Fast I/O operations are placeholders. This is safe but leaves performance on the IRP path.
