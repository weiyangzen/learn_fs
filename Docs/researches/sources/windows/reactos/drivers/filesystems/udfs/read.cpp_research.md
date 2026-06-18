# File Research: sources/windows/reactos/drivers/filesystems/udfs/read.cpp

## Role

`read.cpp` implements read dispatch for the UDF filesystem driver, including normal cached reads, noncached/direct reads, volume reads, paging I/O resource handling, stack-overflow read posting, user-buffer MDL management, and MDL read-completion support.

## Dispatch And Stack-Overflow Handling

`UDFRead()` is the top-level `IRP_MJ_READ` handler. It enters the filesystem, establishes top-level IRP state, allocates a `UDFIrpContext`, calls `UDFCommonRead()`, and delegates exceptions to the shared UDF exception path.

`UDFCommonRead()` checks top-level IRP markers, handles `IRP_MN_COMPLETE` by calling `UDFMdlComplete()`, returns pending for DPC reads, decodes file object/CCB/FCB/VCB, rejects deleted FCBs, and posts through `UDFPostStackOverflowRead()` when remaining kernel stack is below `OVERFLOW_READ_THRESHHOLD`. The overflow helper uses `FsRtlPostStackOverflow()` and `UDFStackOverflowRead()` to retry in a safer context while holding the relevant file resource shared.

## File And Volume Read Behavior

For volume FCB reads, the code forces blocking mode, performs delayed-close and flush work when IRP context flags request it, acquires the VCB resource shared, locks/maps the caller buffer, and reads through either `UDFReadData()` for mounted volumes or `UDFTRead()` for raw/unmounted access.

For file reads, it handles `FILE_USE_FILE_POINTER_POSITION`, rejects directory reads, checks byte-range locks for nonpaging reads, validates/truncates reads against file size, refreshes Fast I/O possibility, and updates access notifications for cached non-volume reads.

Cached reads initialize the cache map on first use with current FCB sizes and UDF cache callbacks, set read-ahead granularity, reject MDL-read requests with `STATUS_INVALID_PARAMETER`, then use `CcCopyRead()`.

Noncached reads flush cached data when needed for coherency, acquire paging I/O resources, lock and map the caller buffer, and call `UDFReadFile__()` with cache-lock awareness. If data is already locked in the driver's fast cache and the request initially cannot wait, it temporarily allows waiting and releases the direct cache lock afterward through `WCacheEODirect__()`.

## Buffer And MDL Helpers

- `UDFGetCallersBuffer()` maps an existing IRP MDL, maps a driver-created MDL from the IRP context, returns a transition buffer when that optional mode is enabled, or falls back to `Irp->UserBuffer`.
- `UDFLockCallersBuffer()` allocates an MDL for the user buffer when one is not present, probes and locks pages with read/write access inverted according to I/O direction, stores the MDL on the IRP, and marks the IRP context as buffer-locked.
- `UDFUnlockCallersBuffer()` flushes I/O buffers and clears context-owned MDL state, relying on I/O completion to unlock/free the MDL in the normal path.
- `UDFMdlComplete()` releases Cache Manager MDLs with `CcMdlReadComplete()` or `CcMdlWriteComplete()`, clears `Irp->MdlAddress`, releases the IRP context, and completes the IRP.

## Completion Semantics

The finalizer releases acquired resources, posts pending work when blocking/resource acquisition was not possible, advances `FileObject->CurrentByteOffset` for successful synchronous nonpaging reads, marks successful nonpaging reads as fast-I/O reads and accessed CCBs, fills `IoStatus`, releases the IRP context, and completes the IRP.

## Dependencies

This file depends on core UDF FCB/CCB/VCB structures, byte-range lock state, resource wrappers, cache manager APIs, MDL/page-locking APIs, UDF physical/logical read helpers, write cache helpers, delayed-close/flush flags, notification helpers, and the shared exception/posting infrastructure.

## Notable Risks

- MDL read support is explicitly disabled by returning `STATUS_INVALID_PARAMETER` for `IRP_MN_MDL` cached reads, while MDL completion support still exists.
- Buffer locking and unlocking rely on IoCompleteRequest to finish MDL cleanup for context-owned MDLs; ownership mistakes can leak or corrupt MDL state.
- Noncached cache coherency depends on targeted `CcFlushCache()` calls and paging-resource serialization, with several older synchronization blocks commented out.
- The read path has many pending/posting exits, so resource-acquisition flags and `PtrIrpContext` ownership must remain exact when changing the function.
