# File Research: sources/windows/reactos/drivers/filesystems/udfs/write.cpp

This file implements the UDF `IRP_MJ_WRITE` dispatch path, deferred write callback, and cache purge helper. It is excluded when `UDF_READ_ONLY_BUILD` is defined.

Key functions:
- `UDFWrite`
  - Top-level write dispatch wrapper.
  - Enters filesystem context, sets top-level IRP state, allocates IRP context, calls `UDFCommonWrite`, handles exceptions, and exits filesystem context.
- `UDFCommonWrite`
  - Handles MDL write completion and DPC-posting cases.
  - Resolves CCB, FCB, VCB, and NT-required FCB state.
  - Rejects deleted files, read-only media/volumes, directories, shutdown volumes, and file-lock conflicts.
  - Supports raw volume writes only when the volume is locked; flushes logical state, locks caller buffer, marks unsafe IOCTL/serial change, and writes through `UDFTWrite`.
  - Applies verification back pressure using `VerifyCtx` queue/item counts.
  - Uses `CcCanIWrite`/`CcDeferWrite` for cached-write throttling.
  - Handles page-file writes as noncached I/O.
  - Interprets `FILE_WRITE_TO_END_OF_FILE` and `FILE_USE_FILE_POINTER_POSITION`.
  - Truncates paging writes beyond EOF and prevents paging I/O from extending file size.
  - Maintains cached/noncached coherency by flushing and purging cache for overlapping noncached writes.
  - Acquires `MainResource`, `PagingIoResource`, and sometimes `VCBResource` according to cached, noncached, paging, lazy-writer, and extension cases.
  - Extends allocation via `UDFResizeFile__`, updates common FCB header sizes, calls `CcSetFileSizes`, and zeroes new gaps with `UDFZeroDataEx`.
  - Initializes system cache maps for first cached writes and uses `CcCopyWrite` for cached writes.
  - Performs direct physical writes through `UDFWriteFile__` for noncached writes.
  - Updates current byte offset, CCB/FO modified flags, file-size-changed state, directory-index file size, and valid data length on success.
  - Posts pending requests with locked buffers and preserved resource-acquired flags where needed.
- `UDFDeferredWriteCallBack`
  - Called by the cache manager to repost deferred write IRPs to UDF’s worker path.
- `UDFPurgeCacheEx_`
  - Purges cache ranges after sparse/unrecorded updates.
  - Optionally uses `CcCopyWrite` with `Vcb->ZBuffer` to zero partial page fragments before purging.
  - Processes large ranges in `PURGE_BLOCK_SZ` chunks and advances valid data length when appropriate.

Notable design points:
- The write path has separate behavior for raw volume writes, cached file writes, noncached file writes, paging I/O, lazy-writer recursion, and write-through recursion.
- File extension is done before cache-manager size publication so allocation failures can still be reported.
- Verification pressure can force waiting before more writes enter the system cache.
- MDL write is effectively unsupported in the cached path: the code returns `STATUS_INVALID_PARAMETER`.
- Raw volume writes deliberately mark the mounted volume unsafe for future quick verification and decrement the serial number to force remount behavior for tools such as check utilities.
