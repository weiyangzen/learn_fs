# File Research: sources/windows/windows-driver-samples/filesys/fastfat/cleanup.c

## Purpose

`cleanup.c` implements FastFAT handling for `IRP_MJ_CLEANUP`, the operation issued when the last user handle to a file object is closed. The file explicitly distinguishes cleanup from close: cleanup makes the file/directory available to other users and performs user-visible teardown, while the FCB/DCB can remain alive because memory manager or cache manager references may still exist.

The implementation covers:

- FSD dispatch entry for cleanup.
- Shared cleanup logic for file, directory, volume, metadata, and unopened objects.
- Delete-on-close processing.
- Share access removal.
- Cache map uninitialization and truncation coordination.
- File-lock release.
- Deferred-flush media handling.
- Oplock cleanup and delete-on-close oplock breaks for Windows 8+.
- Volume auto-unlock on cleanup of the locking handle.

## Main Entry Points

### `FatFsdCleanup`

Lines 47-139 implement the dispatch routine for `IRP_MJ_CLEANUP`.

Control flow:

1. If the request targets the filesystem device object rather than a mounted volume device object, it completes the IRP with `STATUS_SUCCESS`.
2. Enters filesystem context with `FsRtlEnterFileSystem`.
3. Marks/checks top-level IRP state using `FatIsIrpTopLevel`.
4. Creates an IRP context with blocking allowed via `FatCreateIrpContext(Irp, TRUE)`.
5. Calls `FatCommonCleanup`.
6. Routes exceptions through `FatExceptionFilter` and `FatProcessException`.
7. Clears top-level IRP state when owned and exits filesystem context.

This routine is a thin wrapper; all substantive cleanup behavior is in `FatCommonCleanup`.

### `FatCommonCleanup`

Lines 142-1154 implement common cleanup semantics.

Inputs are decoded from the IRP stack file object using `FatDecodeFileObject`, yielding:

- `TypeOfOpen`
- `Vcb`
- `Fcb`
- `Ccb`

The routine handles all open types, updates FCB/VCB state, and completes the IRP except when an oplock break returns `STATUS_PENDING`.

### `FatAutoUnlock`

Lines 1156-1178 clears volume lock state under the VPB spin lock.

It clears `VPB_LOCKED`, `VPB_DIRECT_WRITES_ALLOWED`, `VCB_STATE_FLAG_LOCKED`, and `Vcb->FileObjectWithVcbLocked`.

## Cleanup Flow

### Unopened File Object

If `FatDecodeFileObject` returns `UnopenedFileObject`, cleanup immediately completes successfully. The comments identify this as a special case during VCB initialization and stream file object creation.

### Repeated Cleanup

If `FO_CLEANUP_COMPLETE` is already set, cleanup does not repeat full teardown. It only performs a deferred flush for modified user file opens on deferred-flush, writable media, then completes successfully.

This makes cleanup idempotent for repeated entry paths while preserving flush behavior that may still be required.

### Resource Acquisition

For `UserFileOpen` and `UserDirectoryOpen`, the FCB is acquired exclusive because cleanup may alter allocation or call `CcUninitializeCacheMap`.

If delete-on-close may become the final close-visible cleanup action, the routine drops the FCB, acquires the VCB exclusive first, then reacquires the FCB. This preserves VCB-before-FCB lock ordering for deletion paths.

For `UserVolumeOpen`, the VCB is acquired exclusive.

A `finally` block releases any acquired FCB/VCB resources, sends volume unlock notification if needed, and completes the IRP on normal non-pending termination.

## Delete-On-Close Handling

Cleanup transfers delete-on-close state from the CCB to the FCB:

- If `CCB_FLAG_DELETE_ON_CLOSE` is set, it sets `FCB_STATE_DELETE_ON_CLOSE`.
- It clears the CCB flag to avoid repeated oplock break attempts on re-entry.
- It marks `ProcessingDeleteOnClose`.

For directories, it notifies the directory change package when delete-on-close is observed.

On Windows 8+, if processing delete-on-close for an oplockable file or empty directory, `FsRtlCheckOplockEx` is called with `OPLOCK_FLAG_CLOSING_DELETE_ON_CLOSE`. If it returns `STATUS_PENDING`, the IRP context is marked with `IRP_CONTEXT_FLAG_CLEANUP_BREAKING_OPLOCK`, and cleanup exits pending.

### Directory Delete-On-Close

For `UserDirectoryOpen`, after updating the dirent from the FCB, the routine checks:

- Last unclean handle: `Fcb->UncleanCount == 1`
- Node is a DCB
- FCB is marked delete-on-close
- FCB condition is good
- Volume is not write-protected

If the directory is not empty, delete-on-close is cleared. If it is empty:

1. Save delete context fields: file size and first cluster.
2. Acquire paging I/O resource.
3. Set file size to zero.
4. Truncate allocation to zero.
5. If allocation reaches zero, tunnel the name, delete the dirent, and report `FILE_ACTION_REMOVED`.
6. Remove names from FastFAT name tables so a same-name recreate does not collide before close arrives.
7. On Windows 8+, break the parent directory oplock with parent/removal flags.

Expected filesystem exceptions in this deletion sequence are caught and converted into reset exception state rather than escaping.

### File Delete-On-Close

For `UserFileOpen`, when this is the final unclean handle and the file is good:

1. If delete-on-close is set and media is writable:
   - Save delete context fields.
   - Acquire paging I/O resource.
   - Set file size and valid data length to zero.
   - Reset `ValidDataToDisk`.
   - Persist file size in the dirent using `FatSetFileSizeInDirent`.
   - Mark `FCB_STATE_TRUNCATE_ON_CLOSE`.

2. Later, if `FCB_STATE_TRUNCATE_ON_CLOSE` is set:
   - Truncate allocation to current file size.
   - Set `TruncateSize` for cache map teardown.
   - Clear `FCB_STATE_TRUNCATE_ON_CLOSE`.

3. If delete-on-close remains set and allocation is zero:
   - Tunnel the name.
   - Delete the dirent.
   - Report file-name removal.

4. Regardless of whether truncation and dirent removal succeeded, if delete-on-close remains set:
   - Remove names from internal lookup structures.
   - On Windows 8+, issue advisory parent directory oplock break.

This code deliberately prioritizes removing the name from in-memory lookup even when on-disk deletion is incomplete, preventing immediate recreate collisions before final close.

## Non-Delete File Finalization

For non-delete final file cleanup, if valid data length is below file size, the routine zeroes the range between VDL and EOF unless the file is a paging file. It uses the greater of `Header.ValidDataLength` and `ValidDataToDisk`, rechecks against file size, calls `FatZeroData`, then advances both VDL and `ValidDataToDisk` to file size.

If the file is cached, `CcSetFileSizes` is called so cache manager state reflects the updated size/VDL relationship and avoids stale optimized zero-page behavior.

## Per-Open-Type Behavior

### `DirectoryFile` and `VirtualVolumeFile`

No share access cleanup is needed. These are internal stream-style opens.

### `UserVolumeOpen`

Handles DASD/volume open cleanup:

- If `CCB_FLAG_COMPLETE_DISMOUNT` is set, calls `FatCheckForDismount`.
- Else, if the handle had write access and modified data, flushes the target device with `FatHijackIrpAndFlushDevice` and marks the real device for verify using `DO_VERIFY_VOLUME`.
- If this file object locked the VCB, calls `FatAutoUnlock` and later sends `FSRTL_VOLUME_UNLOCK`.
- Uses `Vcb->ShareAccess` for share-access removal.

### `EaFile`

No share access cleanup is needed.

### `UserDirectoryOpen`

Major actions:

- Uses `Fcb->ShareAccess`.
- Marks `FCB_STATE_DELAY_CLOSE` when the directory has no remaining useful user or directory-file opens and is not being deleted.
- Clears `FCB_STATE_DENY_DEFRAG` if this CCB set `CCB_FLAG_DENY_DEFRAG`.
- Updates the dirent from FCB while the VCB is good and not shutdown.
- Performs directory delete-on-close logic.
- Decrements `Fcb->UncleanCount`.

### `UserFileOpen`

Major actions:

- Uses `Fcb->ShareAccess`.
- Marks `FCB_STATE_DELAY_CLOSE` for final nonmapped, nonpaging, nondelete, good file opens.
- Clears defrag-denial state owned by this CCB.
- Unlocks all outstanding byte-range locks with `FsRtlFastUnlockAll`.
- Updates dirent when mounted and good.
- Handles delete-on-close or VDL zeroing.
- Truncates allocation when required.
- Deletes dirent and removes names when required.
- Decrements `UncleanCount`; decrements `NonCachedUncleanCount` for noncached file objects.
- If the final cached handle is closing while noncached handles remain, flushes/purges cache to reduce coherency overhead.
- Sets `TruncateSize` to zero for bad FCBs to hint cache teardown should discard everything.
- Calls `CcUninitializeCacheMap`.

## Share Access and Oplocks

After open-type-specific cleanup, if `ShareAccess` is non-null, `IoRemoveShareAccess` is called. This happens during cleanup rather than close because close may be delayed by mapped-file references.

For user file opens, and for user directory opens on Windows 8+, cleanup calls `FsRtlCheckOplock` to coordinate cleanup with oplock state. Cleanup is allowed to proceed immediately. It then recomputes `Header.IsFastIoPossible`.

Delete-on-close uses stronger Windows 8+ oplock handling via `FsRtlCheckOplockEx`, including a possible pending return before actual deletion proceeds.

## Cache and Flush Behavior

Cache manager interactions include:

- `CcSetFileSizes` after explicit zeroing to EOF.
- `CcFlushCache` and `CcPurgeCacheSection` when cached handles give way to remaining noncached handles.
- `CcUninitializeCacheMap` during user file cleanup, with truncation hint if applicable.

Deferred flush media logic near the end checks `VCB_STATE_FLAG_DEFERRED_FLUSH` and writable media. It flushes modified user files with `FatFlushFile`. If needed, it flushes FAT state via `FatFlushFat` and also flushes the parent directory. Failure is normalized and raised.

Repeated cleanup also uses deferred file flush for modified user files.

## Locking and Synchronization

Important synchronization mechanisms:

- FCB exclusive acquisition for user file/directory cleanup.
- VCB exclusive acquisition for volume cleanup and final delete-on-close paths.
- Paging I/O resource around direct file-size/VDL changes.
- VPB spin lock in `FatAutoUnlock`.
- Cache manager synchronization through flush, purge, and uninitialize calls.
- `try/finally` cleanup around acquired resources.

The code is careful about lock ordering when deletion may need both VCB and FCB: it reacquires in VCB-first order.

## Error Handling

The file uses structured exception handling heavily:

- Top-level dispatch catches through `FatExceptionFilter` and `FatProcessException`.
- `FatVerifyFcb` exceptions expected by FsRtl are swallowed after `FatResetExceptionState`.
- Delete/truncate/dirent update sequences catch expected exceptions and reset exception state.
- Deferred flush failures are normalized and raised.
- `finally` ensures resources are released and IRP completion occurs unless pending.

The delete-on-close code often continues after expected errors because by cleanup time the user-visible close state cannot be fully rolled back.

## Key State Mutations

Important FCB/CCB/VCB/FileObject state touched:

- `FO_CLEANUP_COMPLETE`
- `FO_FILE_MODIFIED`
- `CCB_FLAG_DELETE_ON_CLOSE`
- `CCB_FLAG_DENY_DEFRAG`
- `FCB_STATE_DELETE_ON_CLOSE`
- `FCB_STATE_DELAY_CLOSE`
- `FCB_STATE_DENY_DEFRAG`
- `FCB_STATE_TRUNCATE_ON_CLOSE`
- `FCB_STATE_FLUSH_FAT`
- `VCB_STATE_FLAG_DEFERRED_FLUSH`
- `VCB_STATE_FLAG_WRITE_PROTECTED`
- `VCB_STATE_FLAG_LOCKED`
- `VCB_STATE_FLAG_SHUTDOWN`
- `UncleanCount`
- `NonCachedUncleanCount`
- `ValidDataToDisk`
- `Header.FileSize`
- `Header.ValidDataLength`

## Relationship to `close.c`

This file performs handle-level cleanup and can mark FCBs for delayed close with `FCB_STATE_DELAY_CLOSE`. `close.c` later observes that flag and can queue actual object teardown to the delayed close worker. Cleanup also removes share access early because the close IRP may not arrive until later due to mapped sections or cache manager references.
