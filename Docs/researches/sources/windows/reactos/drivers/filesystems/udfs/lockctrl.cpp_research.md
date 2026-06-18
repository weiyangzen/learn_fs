# File Research: sources/windows/reactos/drivers/filesystems/udfs/lockctrl.cpp

## Role

`lockctrl.cpp` implements byte-range lock handling for the ReactOS UDF filesystem driver. It covers the normal `IRP_MJ_LOCK_CONTROL` dispatch path plus Fast I/O callbacks for lock and unlock operations.

## Core Behavior

- `UDFLockControl()` is the top-level dispatch entry. It enters the filesystem, sets top-level IRP state, allocates a `UDFIrpContext`, calls `UDFCommonLockControl()`, and routes exceptions through the shared UDF exception filter/handler.
- `UDFCommonLockControl()` validates the file object, CCB, and FCB, rejects volume and directory FCBs, acquires the file's main resource exclusively, and delegates actual byte-range lock processing to `FsRtlProcessFileLock()`.
- If the main resource cannot be acquired in the current wait mode, the IRP is posted through `UDFPostRequest()` and returns pending.
- Fast I/O lock/unlock callbacks (`UDFFastLock`, `UDFFastUnlockSingle`, `UDFFastUnlockAll`, `UDFFastUnlockAllByKey`) decode the FCB/CCB, reject directories and volume opens, call the corresponding `FsRtlFast*` lock routines, and refresh `CommonFCBHeader.IsFastIoPossible`.

## Synchronization And State

Normal lock-control IRPs use `NtReqFcb->MainResource` exclusively around `FsRtlProcessFileLock()`. Fast unlock-all paths take the main resource shared, while the fast lock and fast unlock-single paths contain commented-out resource acquisition, so they rely mainly on the FsRtl file-lock package and surrounding Fast I/O assumptions.

The shared byte-range lock state lives in `NtReqFcb->FileLock`.

## Dependencies

This file depends on the UDF dispatch framework (`UDFAllocateIrpContext`, `UDFReleaseIrpContext`, `UDFPostRequest`, exception handling), FCB/CCB structures, resource wrappers, `UDFIsFastIoPossible()`, and Windows FsRtl file-lock routines.

## Notable Risks

- Fast lock and single-unlock paths do not currently acquire the FCB resource despite comments indicating that they should, which makes their safety depend on FsRtl lock internals and stable FCB lifetime from the caller.
- Directory and volume lock attempts complete as `STATUS_INVALID_PARAMETER`, so callers expecting long-path fallback receive a completed failure.
- `UDF_BUG_CHECK_ID` is set to `UDF_FILE_SHUTDOWN`, which appears inconsistent with the file's lock-control role.
