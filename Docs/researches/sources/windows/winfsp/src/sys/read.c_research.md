# File Research: sources/windows/winfsp/src/sys/read.c

## Purpose

`read.c` implements WinFsp read handling for fast I/O, cached IRP reads, noncached IRP reads, read request preparation for user mode, and read completion.

## Main Contents

- `FspFastIoRead`
- `FspFsvolRead`
- `FspFsvolReadCached`
- `FspFsvolReadNonCached`
- `FspFsvolReadPrepare`
- `FspFsvolReadComplete`
- `FspFsvolReadNonCachedRequestFini`
- `FspRead`

## Fast I/O Path

`FspFastIoRead`:

- Validates the file node.
- Rejects directories.
- Succeeds immediately on zero-length reads.
- Requires `FO_CACHE_SUPPORTED` and an existing private cache map.
- Acquires the file node main resource shared.
- Rejects fast I/O if oplocks or byte-range locks block it.
- Trims reads to file size because cache manager reads cannot extend beyond EOF.
- Calls `FspCcCopyRead`.
- Sets `FO_FILE_FAST_IO_READ`.
- Updates current byte offset for successful synchronous-style fast reads.

## Dispatch Path

`FspFsvolRead`:

- Handles `IRP_MN_COMPLETE` for MDL read completion through `FspCcMdlReadComplete`.
- Rejects invalid file nodes and directories.
- Succeeds immediately on zero-length reads.
- Chooses cached I/O when caching is supported and the IRP is neither paging nor no-cache.
- Otherwise uses noncached handling.

## Cached Reads

`FspFsvolReadCached`:

- Requires top-level IRP.
- Acquires file-node main shared, with work-queue repost if it cannot wait.
- Performs asynchronous oplock checks.
- Checks file locks.
- Trims the read to file size.
- Initializes the cache map if needed using current file information.
- Uses either `FspCcCopyRead` or `FspCcMdlRead`.
- Reposts on cache-manager `STATUS_PENDING`.
- Updates current file offset for synchronous I/O.

## Noncached Reads

`FspFsvolReadNonCached`:

- Rejects MDL minor requests.
- Locks the user buffer for write access.
- Acquires file-node full shared.
- Performs oplock and file-lock checks for non-paging reads.
- If reading noncached from a cached file, flushes and purges relevant cached data under exclusive full acquisition.
- During create-section activity, trims reads to file size to avoid bugchecks if the user-mode filesystem reports inconsistent sizes.
- Creates or resets a `FSP_FSCTL_TRANSACT_REQ`.
- Fills `FspFsctlTransactReadKind` with user contexts, offset, length, and key.
- Sets file-node ownership to the request and posts to the IOQ.
- Updates filesystem statistics, distinguishing paging/user-file reads from noncached reads.

## User-Mode Preparation

`FspFsvolReadPrepare` chooses how user mode receives the target buffer:

- If `FspReadIrpShouldUseProcessBuffer` returns true:
  - Verifies the IRP MDL has a system address.
  - Acquires a reusable process buffer.
  - References the current process.
  - Stores the user-mode address in the request.
  - Stores cookie, address, and process in request context.
- Otherwise:
  - Creates a safe MDL for unaligned edge pages if needed.
  - Maps locked pages into user mode.
  - References the current process.
  - Stores safe MDL, address, and process in request context.

## Completion and Cleanup

`FspFsvolReadComplete`:

- Propagates user-mode failure status.
- Validates that returned byte count does not exceed requested length.
- If a process buffer was used, copies returned bytes back into the IRP MDL system address.
- If a safe MDL was used, copies edge pages back.
- Updates current byte offset for synchronous non-paging top-level reads.
- Resets the request and sets `IoStatus.Information`.

`FspFsvolReadNonCachedRequestFini`:

- Releases process buffers or unmaps user-mode MDL mappings in the original process context.
- Dereferences the process object.
- Deletes safe MDLs.
- Releases file-node request ownership.

## Notable Details

- Cached reads rely on `FileInfoTimeout` being infinite, asserted before using cached file information.
- Process-buffer context encodes the reusable-buffer flag in the low bit of `RequestCookie`.
- The noncached path is also used for paging I/O, but skips oplock and byte-range lock checks for paging reads.
- Completion treats oversized user-mode read responses as `STATUS_INTERNAL_ERROR`.
