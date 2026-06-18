# File Research: sources/windows/windows-driver-samples/filesys/fastfat/lockctrl.c

## Purpose
Implements FAT byte-range lock control for both IRP dispatch and Fast I/O callbacks. It bridges Windows file-lock APIs to `FsRtl` lock routines while preserving FAT FCB synchronization and oplock semantics.

## Main Entry Points
- `FatFsdLockControl`: FSD dispatch routine for `IRP_MJ_LOCK_CONTROL`.
- `FatCommonLockControl`: common IRP path for lock and unlock operations.
- `FatFastLock`: Fast I/O lock callback.
- `FatFastUnlockSingle`: Fast I/O single-range unlock callback.
- `FatFastUnlockAll`: Fast I/O unlock-all callback.
- `FatFastUnlockAllByKey`: Fast I/O unlock-all-by-key callback.

## Behavior
`FatFsdLockControl` enters the filesystem, establishes top-level IRP state, creates an IRP context with wait behavior based on the IRP, and delegates to `FatCommonLockControl`. Exceptions are routed through FAT’s standard exception filter and processor.

All lock operations are valid only for `UserFileOpen`. Volume, directory, metadata, or unrecognized opens are rejected with `STATUS_INVALID_PARAMETER`.

The Fast I/O paths decode the file object, acquire or use FCB synchronization as needed, check whether oplocks allow the fast operation, then call the matching `FsRtlFast*` file-lock helper. On success they recompute `Fcb->Header.IsFastIoPossible` via `FatIsFastIoPossible`.

`FatCommonLockControl` acquires the FCB shared, checks oplocks, calls `FsRtlProcessFileLock`, updates Fast I/O eligibility, and completes the IRP context unless the IRP was posted by oplock handling.

## Synchronization And Oplocks
- Uses shared FCB acquisition for common IRP lock control.
- Fast lock uses `ExAcquireResourceSharedLite` directly on `Fcb->Header.Resource`.
- Fast unlock single checks oplock state but does not acquire the FCB resource in this file, unlike unlock-all variants.
- For Windows 8 and later, oplock checks are narrowed to lock operations within allocation size or unlock operations that may unblock waiting locks.
- Oplock-posted IRPs are not completed in the local finally path.

## Dependencies
- `FatDecodeFileObject`
- `FatCreateIrpContext`
- `FatAcquireSharedFcb`
- `FatFsdPostRequest`
- `FatGetFcbOplock`
- `FatOplockComplete`
- `FatCompleteRequest`
- `FsRtlFastLock`
- `FsRtlFastUnlockSingle`
- `FsRtlFastUnlockAll`
- `FsRtlFastUnlockAllByKey`
- `FsRtlProcessFileLock`
- `FsRtlCheckOplock`

## Important Notes
This file is almost entirely policy glue around `FsRtl` byte-range locking. The FAT-specific parts are open-type validation, FCB resource management, oplock mediation, request posting, and Fast I/O eligibility refresh.
