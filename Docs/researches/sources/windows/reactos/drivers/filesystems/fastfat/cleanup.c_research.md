# File Research: sources/windows/reactos/drivers/filesystems/fastfat/cleanup.c

## Purpose

`cleanup.c` implements FastFAT `IRP_MJ_CLEANUP`, the handle-close phase that runs when the last user handle for a file object is closed. This is where FastFAT releases share access, drains locks and directory notifications tied to the handle, applies delete-on-close semantics, writes final directory-entry state, tears down cache maps for the closing file object, optionally flushes deferred-flush media, and marks the file object with `FO_CLEANUP_COMPLETE`. The FCB/DCB can remain alive after cleanup because section objects, cache maps, or other references may still exist; final structure teardown is handled later by close.

## Key Entry Points

- `FatFsdCleanup`
  - Top-level dispatch routine for cleanup IRPs.
  - Immediately succeeds cleanup sent to the filesystem device object instead of a mounted volume device object.
  - Enters the filesystem, records/restores top-level IRP state, builds a waitable `IRP_CONTEXT`, calls `FatCommonCleanup`, and routes exceptions through `FatExceptionFilter` / `FatProcessException`.

- `FatCommonCleanup`
  - Common cleanup implementation for all FastFAT open types.
  - Decodes the file object into `TypeOfOpen`, `Vcb`, `Fcb`, and `Ccb`.
  - Handles unopened file objects, repeated cleanup calls, user volume opens, user directory opens, user file opens, internal stream opens, and EA file opens.
  - Owns the main delete-on-close, truncate-on-close, share-access removal, oplock cleanup, unclean-count decrement, cache uninitialization, and deferred flush behavior.

- `FatAutoUnlock`
  - Clears `VPB_LOCKED`, `VPB_DIRECT_WRITES_ALLOWED`, `VCB_STATE_FLAG_LOCKED`, and `FileObjectWithVcbLocked` while holding the VPB spin lock.
  - Used when a cleanup closes the volume handle that locked the volume.

## Cleanup Flow

- Repeated cleanup detection:
  - If `FO_CLEANUP_COMPLETE` is already set, the routine only performs a deferred-flush file flush when the volume requires it, the file object was modified, the volume is writable, and this is a `UserFileOpen`.
  - The IRP is then completed successfully.

- Locking setup:
  - User file and user directory opens acquire the FCB exclusively.
  - If a last-handle delete-on-close may actually remove the object, the code drops the FCB, acquires the VCB exclusively, then reacquires the FCB to preserve the global-to-volume-to-file lock ordering needed for deletion.
  - User volume opens acquire the VCB exclusively.

- Delete-on-close transfer:
  - `CCB_FLAG_DELETE_ON_CLOSE` is moved to `FCB_STATE_DELETE_ON_CLOSE` early, then cleared from the CCB.
  - This prevents repeated oplock break attempts if cleanup gets reentered or reposted.
  - For directories, the directory notify package is told that the object is being deleted.

- Verification:
  - If an FCB is present, `FatVerifyFcb` is called inside expected-status exception handling.
  - Expected failures reset exception state so cleanup can still release resources and finish best-effort handle cleanup.

## Open-Type Behavior

- `DirectoryFile` and `VirtualVolumeFile`
  - No share access cleanup is needed.
  - These internal stream-like objects do not run user cleanup semantics.

- `UserVolumeOpen`
  - Completes a pending dismount if `CCB_FLAG_COMPLETE_DISMOUNT` is set.
  - If a writable volume handle modified the volume, it flushes the target device through `FatHijackIrpAndFlushDevice` and sets `DO_VERIFY_VOLUME`.
  - If this file object owns the volume lock, `FatAutoUnlock` releases it and a volume unlock notification is sent after locks are released.
  - Uses `Vcb->ShareAccess`.

- `EaFile`
  - No share access cleanup.

- `UserDirectoryOpen`
  - Calls `FsRtlNotifyCleanup` for notify IRPs tied to this directory handle.
  - Uses `Fcb->ShareAccess`.
  - Marks `FCB_STATE_DELAY_CLOSE` when this is the last unclean and only open directory handle, no internal directory-file opens exist, the directory is not delete-on-close, and the FCB is good.
  - Clears deny-defrag state when this CCB was the handle that set it.
  - Updates the on-disk dirent from the FCB while the volume is mounted and not shutting down.
  - If this is the last unclean handle for a delete-on-close non-root directory and the directory is empty, it truncates allocation to zero, tunnels/removes the directory entry, reports `FILE_ACTION_REMOVED`, removes names from the name table, and breaks the parent directory oplock on Windows 8+ paths.
  - If the directory is not empty, delete-on-close is cleared.
  - Decrements `Fcb->UncleanCount`.

- `UserFileOpen`
  - Uses `Fcb->ShareAccess`.
  - Marks `FCB_STATE_DELAY_CLOSE` when there are no data/image sections, this is the only open/unclean reference, the file is not delete-on-close or a paging file, and the FCB is good.
  - Clears deny-defrag state when owned by this CCB.
  - Unlocks all byte-range locks for this file object with `FsRtlFastUnlockAll`.
  - Updates the directory entry when the mounted volume and FCB are good.
  - On the last unclean handle:
    - For delete-on-close, records delete context, sets file size, VDL, and `ValidDataToDisk` to zero under the paging-I/O resource, writes the size to the dirent best-effort, and sets `FCB_STATE_TRUNCATE_ON_CLOSE`.
    - Otherwise, if valid data length is below file size, zeroes the tail from VDL to file size, advances VDL/`ValidDataToDisk`, and updates cache-manager file sizes when cached.
    - If truncate-on-close is set, truncates allocation to the current file size, records a truncate size for cache-map uninitialization, and clears the truncate flag.
    - If delete-on-close and allocation is now zero, tunnels and deletes the dirent, then reports `FILE_ACTION_REMOVED`.
    - Removes names for delete-on-close even if truncation/deletion could not fully complete, preventing same-name recreate collisions before final close.
  - Decrements `UncleanCount` and, for noncached handles, `NonCachedUncleanCount`.
  - If the last cached handle is closing while noncached handles remain, flushes and purges the cache section to reduce later cached/noncached coherency overhead.
  - Passes `FatLargeZero` as the cache truncation hint if the FCB is bad.
  - Calls `CcUninitializeCacheMap` for the closing file object.

## Oplock and Notification Behavior

- On Windows 8+ builds, cleanup for delete-on-close files or empty directories checks `FsRtlCheckOplockEx` with `OPLOCK_FLAG_CLOSING_DELETE_ON_CLOSE`.
- If the oplock break returns `STATUS_PENDING`, cleanup marks `IRP_CONTEXT_FLAG_CLEANUP_BREAKING_OPLOCK` and exits without completing the IRP in the finalizer.
- After user file cleanup, and on Windows 8+ also after user directory cleanup, the code calls `FsRtlCheckOplock` for normal cleanup coordination and recomputes `Header.IsFastIoPossible`.
- Parent directory oplock breaks after name removal are advisory; the code asserts they do not pend.
- Directory/file delete notifications are reported through `FatNotifyReportChange`.
- Volume unlock is reported through `FsRtlNotifyVolumeEvent` after resources are released.

## Deferred Flush and Cache Behavior

- The file distinguishes normal cleanup work from deferred-flush media cleanup. On deferred-flush writable media:
  - Modified user files are flushed with `FatFlushFile`.
  - If the FCB has `FCB_STATE_FLUSH_FAT`, non-FAT12 volumes flush the FAT and then flush the parent directory if present.
  - Flush errors are normalized and raised.
- `FatUnpinRepinnedBcbs` runs before deferred media flush processing.
- Cache map teardown is central for user-file cleanup and is used with a truncate hint after truncate-on-close so truncated pages are discarded.

## Dependencies and Interactions

- Depends on core FastFAT types and helpers from `fatprocs.h`: file-object decoding, FCB/VCB locking, exception handling, dirent update/delete, allocation truncation, tunneling, notification, oplock lookup, cache flushing, and request completion.
- Coordinates with Windows kernel subsystems:
  - I/O manager file object flags and share access.
  - FSRTL notify, oplock, and byte-range-lock packages.
  - Cache manager file-size, flush, purge, and uninitialize operations.
  - VPB spin-lock state for volume unlock.
- The resulting FCB/DCB lifetime state feeds directly into `close.c`, which later consumes delayed-close flags and open-count state.

## Important Invariants

- Cleanup is handle-oriented; close is reference-oriented. This file must make the file object no longer visible as open to user-mode sharing and locking even if the FCB persists.
- `UncleanCount` must be decremented exactly once for user files/directories after per-handle cleanup work.
- Delete-on-close state is intentionally promoted from CCB to FCB before oplock handling to avoid repeated cleanup breaks.
- Name removal on delete-on-close is used as an in-memory namespace correctness step even when on-disk deletion was only partially successful.
- Resource release and IRP completion are centralized in the `finally` block; pending oplock cleanup intentionally skips final completion.

## Notable Risks

- Delete-on-close and truncate-on-close are best-effort around expected disk/verify errors, so later close/dismount behavior must tolerate partially completed deletion state.
- The file depends on careful lock ordering when escalating from FCB-only to VCB+FCB for deletion.
- Cache coherency relies on the VDL zeroing path updating both FCB state and cache-manager sizes; missing that update would allow stale optimized zero-page behavior.
- Parent oplock breaks after name removal are asserted non-pending; if underlying FSRTL behavior changed, this path would need revisiting.
