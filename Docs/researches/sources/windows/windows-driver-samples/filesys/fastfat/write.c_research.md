# File Research: sources/windows/windows-driver-samples/filesys/fastfat/write.c

## Purpose

`write.c` implements the FastFAT write path for `IRP_MJ_WRITE`. It handles:

- FSD write dispatch through `FatFsdWrite`.
- Main write processing through `FatCommonWrite`.
- Special writes to paging files, FAT metadata, raw volumes, normal files, directories, and EA files.
- Cached, noncached, paging, MDL, synchronous, asynchronous, write-through, and write-to-EOF variants.
- EOF and valid-data-length extension.
- FAT allocation growth, cache-manager coherency, oplock/file-lock checks, completion, rollback, and deferred flush work.

This is a core filesystem write-path file, not just sample glue.

## Major Entry Points

### `FatFsdWrite`

`FatFsdWrite` is the dispatch entry for write IRPs.

Key behavior:

- Enters the filesystem with `FsRtlEnterFileSystem`.
- Fast-paths paging-file I/O before creating a normal IRP context:
  - If the target is not the filesystem device object and the FCB is a paging file, it marks the IRP pending and calls `FatPagingFileIo`.
- Creates an `IRP_CONTEXT` with waitability derived from the IRP.
- Handles the modified-page-writer top-level IRP case by temporarily replacing `IoGetTopLevelIrp()` with the actual IRP so write-through behavior works correctly.
- Routes `IRP_MN_COMPLETE` to `FatCompleteMdl`; all other writes go to `FatCommonWrite`.
- Uses the FastFAT exception filter/processor and restores top-level IRP state before leaving the filesystem.

### `FatCommonWrite`

`FatCommonWrite` is the main write implementation. Its inputs are the IRP context and IRP; it derives the rest from the current stack location and file object.

It initializes core state:

- `Wait` from `IRP_CONTEXT_FLAG_WAIT`.
- `PagingIo` from `IRP_PAGING_IO`.
- `NonCachedIo` from `IRP_NOCACHE`.
- `SynchronousIo` from `FO_SYNCHRONOUS_IO`.
- `WriteToEof` from `FILE_WRITE_TO_END_OF_FILE`.
- `TypeOfOpen` via `FatDecodeFileObject`.

It immediately completes zero-length writes with success.

## Cached Write Admission

Before decoding all object-specific cases, the routine throttles cached writes with `CcCanIWrite`. If the cache manager says the write should be deferred, FastFAT:

- Calls `FatPrePostIrp`.
- Sets `IRP_CONTEXT_FLAG_DEFERRED_WRITE`.
- Calls `CcDeferWrite` with `FatAddToWorkque`.
- Returns `STATUS_PENDING`.

This keeps large cached writes from overwhelming the cache manager.

## Range and Context Setup

For ordinary non-paging, non-EOF writes, FastFAT rejects ranges that would require maintaining FAT allocation sizes beyond 32 significant bits by calling `FatIsIoRangeValid`.

For noncached I/O, it creates or reuses a `FAT_IO_CONTEXT`:

- Synchronous noncached I/O can use stack storage.
- Asynchronous noncached I/O allocates nonpaged pool.
- The async context records resource ownership and requested byte count for completion/release logic.

If the volume is already shut down, the write fails with `STATUS_TOO_LATE`.

## Virtual Volume File Writes

`TypeOfOpen == VirtualVolumeFile` is the internal volume file used for FAT metadata.

Important behavior:

- Requires waitable execution; otherwise posts to the FSP.
- If not called by the lazy writer, sets write-through in the IRP context.
- Uses `Vcb->DirtyFatMcb` to find dirty FAT sectors within the requested write range.
- Skips clean runs, writes from the first dirty run through the last dirty run needed, and may include clean bytes for efficiency.
- Builds one `IO_RUN` per FAT copy, mapping the same dirty VBO region to each FAT’s LBO.
- Calls `FatMultipleAsync`, waits with `FatWaitSync`, and on success removes the written range from `DirtyFatMcb`.
- On error, normalizes/raises the status so volume verification/reset can occur.

The invariant is that the dirty FAT MCB alternates clean holes and dirty runs, and must contain an even number of runs.

## Raw Volume Writes

`TypeOfOpen == UserVolumeOpen` handles DASD/raw volume writes.

Key rules:

- Raw volume opens are forced to noncached I/O.
- For disk devices that are not volume-locked, writes are restricted to the reserved area unless:
  - `SL_FORCE_DIRECT_WRITE` is set,
  - the handle performed a complete dismount,
  - or extended DASD I/O is allowed.
- The VCB is verified unless the handle has complete-dismount or format-unit flags.
- A format-unit handle may override verify.
- On the first DASD write per CCB, FastFAT flushes/purges FAT and referenced file objects under exclusive volume synchronization.
- Unless extended DASD I/O is allowed, writes are clipped to visible volume size.
- User buffers are locked, `FO_FILE_MODIFIED` is set, and `FatSingleAsync` issues the disk write.
- Async writes detach the IRP context and return `STATUS_PENDING`.
- Sync writes wait, normalize failures, and update `CurrentByteOffset`.

## User File Writes

`TypeOfOpen == UserFileOpen` is the largest and most complex branch.

### Noncached Coherency

For noncached, non-paging writes to a file that also has a cache map:

- FastFAT acquires the FCB exclusive.
- It pre-acquires the paging I/O resource.
- On newer builds it uses `CcCoherencyFlushAndPurgeCache`; older builds use `CcFlushCache` followed by `CcPurgeCacheSection`.
- It keeps paging I/O held across the noncached write to prevent page faults from observing stale disk data.
- In purge-failure mode for user files, a purge failure returns `STATUS_PURGE_FAILED`.

This is one of the key correctness mechanisms in the file.

### Resource Acquisition

The write path selects resources according to operation type:

- Paging I/O acquires `Header.PagingIoResource` shared and waits for `MoveFileEvent` if present.
- Non-paging I/O normally acquires the FCB shared.
- Async noncached I/O may wait for exclusive waiters and records the acquired resource in the async context.
- If EOF or valid-data extension is needed, the path upgrades to exclusive FCB synchronization.

### Paging I/O Truncation

Paging writes are never allowed to extend file size.

If paging I/O starts beyond EOF:

- It completes successfully with zero bytes.

If it extends beyond EOF:

- `ByteCount` is trimmed to file size.

This prevents cache manager or memory manager page flushes from creating filesystem-visible file growth.

### Lazy Writer and Recursive Write-Through

The routine detects:

- Lazy-writer writes by comparing the current thread with `FcbOrDcb->Specific.Fcb.LazyWriteThread`.
- Recursive synchronous paging writes generated by write-through cached writes.

Lazy-writer writes are blocked from flushing mapped pages beyond safe valid-data regions and are not allowed to perform file-size/VDL extension work.

Recursive write-through writes set `IRP_CONTEXT_FLAG_WRITE_THROUGH` but are also excluded from top-level valid-data extension behavior.

### EOF and Valid Data Extension

The routine follows explicit rules:

- Paging I/O never extends file size.
- Only top-level callers extend valid data length.
- If file size or valid data must grow, the FCB is acquired exclusive.

For write-to-EOF, the actual starting VBO is recalculated after acquiring synchronization and reading current file size.

Before modifying the file, non-paging user writes check:

- Oplocks through `FsRtlCheckOplock`.
- Fast I/O possibility after oplock state changes.
- Byte-range locks through `FsRtlCheckLockForWriteAccess`.

### Allocation Growth

When a write extends file size past allocation size:

- Existing allocation size may first be looked up if it is only a hint.
- FastFAT tries allocation chunking when this is not the first allocation:
  - It computes a multiplier based on free clusters and requested growth.
  - The multiplier is capped at 32.
  - Allocation is capped at the maximum legal FAT file size.
  - If the larger allocation fails with disk full, it falls back to minimum allocation.
- Successful chunked allocation sets `FCB_STATE_TRUNCATE_ON_CLOSE`.
- The FCB file size is updated.
- If the file is cached, `CcSetFileSizes` informs the cache manager.

### Valid Data Handling

The routine decides whether `ExtendingValidData` is needed after final resource and size checks.

It uses `ValidDataToCheck = max(ValidDataToDisk, ValidDataLength)` to determine whether zeroing is needed.

For noncached writes starting beyond valid data, it zeroes the gap with `FatZeroData`, except for lazy-writer and recursive write-through cases.

After a successful write that extends valid data:

- `Header.ValidDataLength` is advanced but never past file size.
- For noncached writes to cached files, `CcSetFileSizes` updates cache-manager state so future cached I/O does not see incorrect zero-page behavior.

## Noncached File Writes

In the noncached branch:

- The write length is rounded up to sector size.
- The start must be sector-aligned.
- If the rounded length differs from requested length, the write must not overwrite valid data past the caller’s byte count; otherwise FastFAT returns `STATUS_NOT_IMPLEMENTED`.
- Gaps beyond valid data are zeroed.
- `WriteFileSizeToDirent` is set so successful extending noncached writes update on-disk directory entry size.
- `FatNonCachedIo` issues the transfer.
- Pending async I/O detaches the IRP and IRP context.
- On success, `IoStatus.Information` is restored to the caller’s original byte count and `ValidDataToDisk` is advanced.

## Cached File Writes

In the cached branch:

- Paging I/O is not expected.
- The cache map is lazily initialized with `FatInitializeCacheMap`.
- Allocation size is validated before cache initialization; if file size exceeds allocation size, FastFAT reports file corruption.
- Read-ahead granularity is set.
- On deferred-flush media:
  - Page-aligned large writes make the file object write-through.
  - Small writes schedule a one-second deferred flush via timer/DPC/work item.
- Gaps beyond valid data are zeroed with `FatZeroData`.
- `WriteFileSizeToDirent` is true only for write-through cached writes.
- Normal cached writes map the user buffer and call `CcCopyWriteEx` or `CcCopyWrite`.
- MDL writes call `CcPrepareMdlWrite`.

## Directory and EA File Writes

`DirectoryFile` and `EaFile` writes are treated as system paging/noncached writes.

Behavior:

- Verifies the FCB/DCB.
- Acquires paging I/O shared, starving exclusive waiters.
- Waits on `MoveFileEvent` if present.
- Sets write-through if not called by the lazy writer.
- Asserts sector alignment and paging/noncached mode.
- Trims writes to file size.
- Issues `FatNonCachedIo`.
- Normalizes failures.

`UserDirectoryOpen` writes are rejected with `STATUS_INVALID_PARAMETER`.

Unknown open types bugcheck because they indicate internal corruption.

## Completion and Rollback

The `try_exit` and `finally` logic is as important as the write branches.

On successful, non-posted completion:

- Updates synchronous current byte offset.
- Sets `FO_FILE_MODIFIED` for non-paging writes.
- If file size was extended and `WriteFileSizeToDirent` is true:
  - Calls `FatSetFileSizeInDirent`.
  - Reports `FILE_NOTIFY_CHANGE_SIZE`.
- If file size was extended but not immediately written to the dirent:
  - Sets `FO_FILE_SIZE_CHANGED`.
- If valid data was extended:
  - Advances `Header.ValidDataLength`.
  - Updates cache manager for noncached writes to cached files.
- Unpins repinned BCBs.

When posting after tentative file-size extension:

- It rolls back `Header.FileSize`.
- Updates the cache manager’s file size pointer if a shared cache map exists.
- Posts with `FatFsdPostRequest`.

On abnormal termination:

- Restores initial file size and valid data length if they were extended.
- Pulls back the cache size pointer if needed.

Finally, it unwinds outstanding async counters, releases FCB and paging resources if still associated with the IRP, and completes non-posted requests.

## Deferred Flush Helpers

### `FatDeferredFlushDpc`

Runs from the timer DPC after a small cached write on deferred-flush media. It initializes and queues a work item to `FatDeferredFlush`.

### `FatDeferredFlush`

Runs in a worker thread and:

- Decodes the file object.
- Sets top-level IRP to `FSRTL_FSP_TOP_LEVEL_IRP`.
- Acquires the FCB exclusive and paging I/O shared.
- Calls `CcFlushCache`.
- Releases resources.
- Clears top-level IRP.
- Dereferences the file object and frees the flush context.

## Important Invariants

- `ValidDataLength <= FileSize <= AllocationSize`.
- Paging I/O must not extend file size.
- Only top-level writes extend valid data length.
- Noncached writes against cached files must force cache coherency before disk I/O.
- FAT metadata writes are tracked and cleaned through `DirtyFatMcb`.
- File-size/VDL changes are rolled back if the path posts or aborts before completion.
- Async noncached writes carry resource-release information in `FAT_IO_CONTEXT`.

## Dependencies

This file depends heavily on FastFAT infrastructure declared elsewhere, including:

- FCB/VCB/CCB structures and open decoding.
- Allocation helpers such as `FatAddFileAllocation`, `FatLookupFileAllocationSize`, and `FatTruncate...`-style close cleanup elsewhere.
- Cache helpers such as `FatInitializeCacheMap`, `FatZeroData`, and `FatUnpinRepinnedBcbs`.
- Device I/O helpers such as `FatSingleAsync`, `FatMultipleAsync`, `FatNonCachedIo`, and `FatWaitSync`.
- Error handling through `FatNormalizeAndRaiseStatus`, `FatRaiseStatus`, and exception filters.
- Notification and dirent update helpers.

## Research Notes

This file is a dense reference for Windows filesystem write-path design. The most reusable patterns are:

- Split dispatch wrapper from common write engine.
- Treat paging writes, cached writes, and noncached writes as separate synchronization domains.
- Keep cache coherency and VDL extension decisions explicit.
- Roll back FCB/cache-manager state when an operation is posted or aborted.
- Use separate paths for raw volume writes and internal metadata writes rather than forcing them through normal file semantics.
