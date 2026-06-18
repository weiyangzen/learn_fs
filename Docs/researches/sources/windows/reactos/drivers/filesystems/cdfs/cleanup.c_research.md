# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cleanup.c

## Purpose

`cleanup.c` implements `IRP_MJ_CLEANUP` for CDFS. Cleanup runs when the last handle to a file object closes, before the file object itself necessarily loses all references.

## Key Contents

- `CdCommonCleanup`
  - Completes immediately if the request targets the filesystem device object rather than a mounted volume.
  - Decodes the file object into `TypeOfOpen`, `Fcb`, and `Ccb`.
  - Ignores unopened and stream file objects.
  - Sets `FO_CLEANUP_COMPLETE` while holding the file resource exclusively so later reads fail through FCB verification.
  - Handles volume opens:
    - If `CCB_FLAG_DISMOUNT_ON_CLOSE`, acquires global data and calls `CdCheckForDismount(..., Force=TRUE)`.
    - If file object was modified, flushes device buffers with `CdHijackIrpAndFlushDevice` and marks the device for verify.
  - Acquires the FCB exclusively for cleanup accounting and handle-state teardown.
  - For directory opens, calls `FsRtlNotifyCleanup`.
  - For file opens:
    - coordinates with oplock cleanup via `FsRtlCheckOplock`
    - unlocks all byte-range locks via `FsRtlFastUnlockAll`
    - uninitializes cache map with `CcUninitializeCacheMap`
    - recalculates fast-I/O state
  - Locks the VCB and decrements cleanup counts.
  - Unlocks the volume if this file object owns `Vcb->VolumeLockFileObject`.
  - Removes share access via `IoRemoveShareAccess`.
  - Sends `FSRTL_VOLUME_UNLOCK` notification if needed.
  - If cleanup count reaches zero on a not-mounted volume, attempts teardown by acquiring CdData, acquiring VCB exclusive, and purging the volume.

## Dependencies and Interactions

- Depends on `CdDecodeFileObject`, `CdAcquireFileExclusive`, `CdAcquireFcbExclusive`, `CdDecrementCleanupCounts`, `CdPurgeVolume`, `CdCheckForDismount`, and volume verify helpers.
- Updates VCB and FCB cleanup counts defined in `cdstruc.h`.
- Interacts with cache manager, oplock package, file-lock package, notify package, and I/O manager VPB lock state.
- Complements `close.c`: cleanup releases handle-visible state, while close releases the file-object reference and may tear down structures.

## Behavioral Notes

- Cleanup is not the final object destruction path; mapped files can keep FCBs alive after cleanup.
- Volume unlock is performed even for implicit volume locks.
- Teardown triggering is conservative: it purges to force closes, then final teardown is expected after the current IRP completes if this file object was the last hold.
- Share access removal happens during cleanup because close may be delayed.
