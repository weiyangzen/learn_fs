# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.cc

## Purpose
`XrdClXCpCtx.cc` implements `XCpCtx`, the coordinator for "extreme copy" multi-source downloads. It owns the replica URL queue, source-thread list, shared sink of downloaded `PageInfo` chunks, block allocation cursor, file-size coordination, completion signaling, and reference-counted lifecycle used by `XCpSrc` workers.

## Important APIs, Types, And Functions
- `XCpCtx::XCpCtx` initializes URL queue, block/chunk/parallelism settings, offsets, condition variables, counters, and optionally calls `SetFileSize`.
- `~XCpCtx` drains remaining sink chunks and frees them through `XCpSrc::DeleteChunk`.
- `GetNextUrl` pops the next replica URL under `pMtx`.
- `WeakestLink` selects the running source with data and the lowest `TransferRate`, excluding a requester, and returns a retained source pointer via `Self()`.
- `PutChunk` pushes a downloaded `PageInfo*` into `pSink`.
- `GetBlock` allocates the next contiguous file range from `pOffset` and `pBlockSize`.
- `SetFileSize` publishes file size, broadcasts waiters, and adjusts `pBlockSize` relative to source parallelism and chunk size.
- `Initialize` creates `pParallelSrc` `XCpSrc` objects and starts their threads.
- `GetChunk` is the consumer-facing method that returns `suContinue` with a chunk, `suRetry` for a null wakeup, `suDone` when all data was received, or `errNoMoreReplicas` when all sources stopped.
- `NotifyIdleSrc`, `AllDone`, and `GetRunning` coordinate idle source wakeups and progress checks.

## Control Flow
After construction, the caller invokes `Initialize`, which creates source objects and starts one thread per source. Each source opens replicas, obtains blocks through `GetBlock`, reads chunks asynchronously, and calls `PutChunk`. The main copy loop repeatedly calls `GetChunk`; it marks the context done once `pDataReceived` equals `pFileSize`, fails if no source is running, otherwise consumes `pSink`. Idle sources use `AllDone` to sleep up to 60 seconds or wake when another source fails and work may be stealable.

## State And Persistence Behavior
`XCpCtx` keeps all state in memory. `pUrls` is destructively consumed. `pOffset` monotonically tracks allocated file ranges. `pFileSize` starts at `-1` until supplied by metalink input or discovered by a source stat. `pDataReceived` tracks bytes delivered to the consumer, not necessarily bytes still queued in `pSink`. `pDone` signals global completion/failure to source threads. `pRefCount`, `pDeleteCV`, and `pDelete` implement cooperative deletion: the creator calls `Delete()`, sources call `Release()`, and destruction waits until source-held references are gone.

## Dependencies And Integration Points
This file depends on `XCpSrc`, `SyncQueue<PageInfo*>`, `XrdSysMutex`, `XrdSysCondVar`, `DefaultEnv::GetLog()`, and XrdCl status constants. It is the bridge between higher-level copy code consuming `PageInfo` chunks and source workers reading from XRootD replicas.

## Risks And Edge Cases
- `GetBlock` assumes a known non-negative `pFileSize`; if called before `SetFileSize`, casting `-1` to `uint64_t` would be wrong. Source initialization sets file size before block allocation when unknown.
- `SetFileSize` can compute `pFileSize / pParallelSrc`; `pParallelSrc` must be nonzero.
- `GetChunk` compares `pDataReceived` to `pFileSize`; duplicate/stolen chunks or size mismatches must be prevented by `XCpSrc` or the completion logic can misfire.
- `AllDone` uses a 60-second timeout as both wakeup and periodic degradation check, which affects responsiveness.
- The lifecycle is manually reference-counted and sensitive to lock ordering documented in the header.

## Test Signals
Test with known and unknown file sizes, no valid replicas, partial source startup failures, zero-byte files, block-size adjustment around chunk boundaries, null wakeups from failed sources, and stealing scenarios where one source fails while holding ongoing work.
