# File Research: sources/windows/reactos/drivers/filesystems/cdfs/lockctrl.c

## Purpose

`lockctrl.c` implements byte-range lock control for CDFS, including IRP-based lock handling and fast I/O lock/unlock callbacks.

## Main IRP Path

`CdCommonLockControl` handles `IRP_MJ_LOCK_CONTROL`. It decodes the file object and accepts only `UserFileOpen`. It checks oplock state with `FsRtlCheckOplock`, verifies the FCB, creates an `FsRtl` file lock if needed, calls `FsRtlProcessFileLock`, recomputes `Fcb->IsFastIoPossible`, completes the request, and returns the status.

## Fast I/O Lock/Unlock Functions

- `CdFastLock`: validates `UserFileOpen`, verifies the FCB, requires fast oplock eligibility, creates a file lock if needed, calls `FsRtlFastLock`, and updates fast I/O state when a lock is granted.
- `CdFastUnlockSingle`: validates `UserFileOpen`, returns `STATUS_RANGE_NOT_LOCKED` if no file lock exists, checks oplock fast-I/O eligibility, calls `FsRtlFastUnlockSingle`, and recomputes fast I/O state when no current locks remain.
- `CdFastUnlockAll`: validates `UserFileOpen`, returns `STATUS_RANGE_NOT_LOCKED` if no file lock exists, checks oplock fast-I/O eligibility, calls `FsRtlFastUnlockAll`, and recomputes fast I/O state.
- `CdFastUnlockAllByKey`: same structure as unlock-all, but calls `FsRtlFastUnlockAllByKey`.

All fast callbacks enter and exit the filesystem around protected work and return `FALSE` when the fast path cannot safely complete, letting the caller fall back to the IRP path.

## Locking Semantics

Only user file opens can use byte-range locks. Directory, volume, stream, or unopened objects are rejected with `STATUS_INVALID_PARAMETER`. The implementation relies on `FsRtl` lock packages for actual range conflict and unlock semantics.

## Fast I/O State

After lock state changes, the file’s `IsFastIoPossible` state is recomputed with `CdIsFastIoPossible`. This ensures cached/fast I/O observes lock and oplock restrictions.

## Dependencies

This file depends on file-object decoding from `filobsup.c`, FCB verification, oplock helpers from `fsctrl.c`/FCB state, `CdCreateFileLock`, `CdGetFcbOplock`, `CdLockFcb`, `CdUnlockFcb`, and Windows `FsRtl` file-lock APIs.

## Research Notes

The file is mostly a thin validation and synchronization layer over `FsRtl` byte-range locking. Its correctness depends on rejecting non-file opens, keeping file-lock allocation synchronized, and updating fast-I/O eligibility after any successful lock-state mutation.
