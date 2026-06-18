# File Research: sources/windows/reactos/drivers/filesystems/fastfat/lockctrl.c

## Scope

This file implements fastfat byte-range lock control. It provides the IRP_MJ_LOCK_CONTROL FSD dispatch entry, fast I/O lock/unlock callbacks, and the common lock-control worker used by FSD and FSP paths. The implementation delegates actual file-lock bookkeeping to FsRtl while enforcing fastfat open-type validation, FCB synchronization, oplock interaction, exception handling, and fast-I/O state updates.

## Public And Internal APIs Covered

- FSD dispatch: `FatFsdLockControl()`.
- Fast I/O callbacks: `FatFastLock()`, `FatFastUnlockSingle()`, `FatFastUnlockAll()`, and `FatFastUnlockAllByKey()`.
- Common IRP worker: `FatCommonLockControl()`.

## Control Flow And Behavior

- `FatFsdLockControl()` enters filesystem context, sets top-level IRP state, creates an IRP context with `CanFsdWait(Irp)`, calls `FatCommonLockControl()`, handles exceptions via `FatExceptionFilter()` and `FatProcessException()`, clears top-level state when this IRP was top level, and exits filesystem context.
- All fast I/O callbacks first decode the file object and accept only `UserFileOpen`; non-file opens are completed in fast path with `STATUS_INVALID_PARAMETER` and `TRUE`, meaning no long-path retry is needed.
- `FatFastLock()` enters filesystem context, acquires the FCB main resource shared, checks `FsRtlOplockIsFastIoPossible()`, then calls `FsRtlFastLock()` with the file's `FILE_LOCK`, target range, process id, key, fail-immediately flag, and exclusive/shared mode. On success it refreshes `Header.IsFastIoPossible`.
- `FatFastUnlockSingle()` validates user-file open and checks oplock fast-I/O possibility, then calls `FsRtlFastUnlockSingle()` and updates fast-I/O state. This routine does not acquire the FCB resource in this ReactOS source, despite comments saying it acquires exclusive access.
- `FatFastUnlockAll()` and `FatFastUnlockAllByKey()` acquire the FCB resource shared, check oplock fast-I/O possibility, call the corresponding FsRtl unlock helper, and update fast-I/O state.
- `FatCommonLockControl()` decodes the file object, rejects non-user-file opens, acquires the FCB shared or posts the request if it cannot acquire, checks oplocks with `FsRtlCheckOplock()` before operations that can interfere, delegates lock/unlock IRP processing to `FsRtlProcessFileLock()`, updates fast-I/O state, completes only the IRP context on normal non-oplock-post completion, and releases the FCB.
- On newer build conditions, the oplock check is limited to locks inside allocation size or unlocks that might grant waiting locks, reducing unnecessary oplock interaction outside meaningful file allocation.

## State And Data Structures

- Per-file lock state is `Fcb->Specific.Fcb.FileLock`.
- Oplock state is accessed through `FatGetFcbOplock(Fcb)`.
- Synchronization uses `Fcb->Header.Resource`; the common path uses fastfat's `FatAcquireSharedFcb()` / `FatReleaseFcb()`, while fast I/O paths use `ExAcquireResourceSharedLite()` directly where present.
- Completion/output state is carried in `IO_STATUS_BLOCK` for fast I/O callbacks and in IRP status for common IRP processing.
- Fast-I/O eligibility is recomputed through `FatIsFastIoPossible(Fcb)` after lock-state changes.

## Dependencies

- NT fast I/O callback contracts for lock and unlock operations.
- FsRtl file-lock package: `FsRtlFastLock()`, `FsRtlFastUnlockSingle()`, `FsRtlFastUnlockAll()`, `FsRtlFastUnlockAllByKey()`, and `FsRtlProcessFileLock()`.
- FsRtl oplock package: `FsRtlOplockIsFastIoPossible()` and `FsRtlCheckOplock()`.
- Fastfat support: file-object decoding, IRP context creation, request posting, exception handling, FCB acquisition/release, oplock completion callback, request completion, and fast-I/O-possible computation.

## Risks And Invariants

- Byte-range locks are valid only for user file opens; volume, directory, and internal opens are rejected.
- Oplock checks must happen before granting locks that can conflict with caching semantics. If an oplock break posts the IRP, the common path must not complete the request.
- Fast I/O callbacks return `FALSE` when oplock state requires the caller to use the normal IRP path.
- FCB resource acquisition must be balanced across exception paths. Most fast I/O unlock callbacks use shared acquisition even though comments refer to exclusive access.
- Updating `IsFastIoPossible` after each successful lock-state change is necessary because active locks can disable fast I/O for later reads/writes.
