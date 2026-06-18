# File Research: sources/windows/windows-driver-samples/filesys/cdfs/lockctrl.c

## Purpose

Implements CDFS byte-range lock handling for both regular IRP dispatch and Fast I/O lock callbacks.

## Main Entry Points

- `CdCommonLockControl`
- `CdFastLock`
- `CdFastUnlockSingle`
- `CdFastUnlockAll`
- `CdFastUnlockAllByKey`

## Key Behavior

`CdCommonLockControl` accepts only `UserFileOpen`. It checks oplock state with `FsRtlCheckOplock`, verifies the FCB, lazily creates `Fcb->FileLock`, then delegates byte-range lock processing to `FsRtlProcessFileLock`. After lock processing it recomputes `Fcb->IsFastIoPossible`.

The fast-path routines decode the file object with `CdFastDecodeFileObject`, reject non-user-file opens with `STATUS_INVALID_PARAMETER`, and avoid the fast path when `CdVerifyFcbOperation(NULL, Fcb)` fails. They wrap FsRtl lock calls in `FsRtlEnterFileSystem` / `FsRtlExitFileSystem`.

`CdFastLock` checks that oplocks permit fast I/O, creates the file-lock object without raising, calls `FsRtlFastLock`, and updates fast-I/O state when needed.

The unlock fast paths return `STATUS_RANGE_NOT_LOCKED` immediately when the FCB has no file-lock package. Otherwise they check oplock fast-I/O eligibility and call the matching FsRtl unlock primitive.

## Dependencies

This module depends on CDFS file-object decode helpers, FCB verification, file-lock allocation in `strucsup.c`, oplock completion/prepost helpers, and FsRtl file-lock APIs.

## Notes and Risks

The fast unlock routines reference `IrpContext` in `CdLockFcb(IrpContext, Fcb)` / `CdUnlockFcb(IrpContext, Fcb)` despite not declaring an `IrpContext` local. In this source as read, that is a compile-time issue unless hidden by non-obvious macro behavior outside this file. The analogous fast-lock routine uses `NULL` there.
