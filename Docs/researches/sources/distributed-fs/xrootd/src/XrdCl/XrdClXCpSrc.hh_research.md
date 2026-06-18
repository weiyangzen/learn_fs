# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.hh

## Purpose
`XrdClXCpSrc.hh` declares `XCpSrc`, a per-replica worker used by extreme copy. It exposes thread lifecycle, reference counting, status/throughput inspection, and chunk cleanup helpers while keeping read, recovery, and stealing mechanics private.

## Important APIs, Types, And Functions
- Public constructor accepts chunk size, async parallelism, optional file size, and the shared `XCpCtx`.
- `Start`, `Stop`, `IsRunning`, `HasData`, `TransferRate`, `Self`, and `Delete` are used by the context and peer sources.
- `DeleteChunk` frees the buffer inside a `PageInfo` and deletes the `PageInfo` object.
- Private methods include `Run`, `StartDownloading`, `Initialize`, `Recover`, `ReadChunks`, `Steal`, `GetWork`, and `ReportResponse`.
- `FilesEqual` compares `File` objects by `LastURL` after stripping CGI query strings, helping separate active-handle responses from failed-handle responses.
- State fields include `pFile`, `pFailed`, `pOngoing`, `pRecovered`, `pReports`, recursive mutex, atomic running flag, and PgRead toggle.

## Control Flow
The public `Start` method spawns a pthread running `Run`. The thread calls `StartDownloading`, then `Delete`, making `XCpSrc` mostly self-owned after start. Async callbacks enter through friend `ChunkHandler`, which can call `ReportResponse`. Source peers and the context coordinate via `HasData`, `TransferRate`, and `Steal`.

## State And Persistence Behavior
`XCpSrc` stores transient transfer state. `pCurrentOffset`/`pBlkEnd` define the assigned block, `pOngoing` tracks issued async reads, `pRecovered` tracks chunks that must be retried or stolen, and `pFailed` defers closing failed file handles until their outstanding callbacks arrive. `pDataTransfered`, `pStartTime`, and `pTransferTime` are used for scheduling/stealing heuristics. No state survives process lifetime.

## Dependencies And Integration Points
The header depends on `XrdClFile.hh`, `SyncQueue`, pthread helpers, and C++ atomics. It forward-declares `XCpCtx`, but its implementation depends on `XCpCtx`, `Utils`, `DefaultEnv`, and XRootD response types. It is an internal part of the copy subsystem rather than a broad public API.

## Risks And Edge Cases
- Manual reference counting plus self-deleting thread flow makes ownership mistakes high impact.
- `Self()` can return `nullptr` if the object is already in destruction, so callers must check retained pointers.
- `DeleteChunk` assumes the `PageInfo` buffer was allocated with `new[] char`, which must match every producer path.
- `pParallel` and `pChunkSize` control memory pressure because each outstanding read allocates a buffer.

## Test Signals
Coverage should include `FilesEqual` with CGI differences, `Self()` during destruction, `HasData` for each work map/cursor condition, `DeleteChunk` ownership conventions, and thread start failure paths.
