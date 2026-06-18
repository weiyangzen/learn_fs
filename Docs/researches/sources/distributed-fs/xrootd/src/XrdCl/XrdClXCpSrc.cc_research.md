# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.cc

## Purpose
`XrdClXCpSrc.cc` implements a source worker for extreme copy. Each `XCpSrc` runs in its own thread, opens one replica at a time, optionally stats the file, reads chunks asynchronously with `File::Read` or `File::PgRead`, reports completed `PageInfo` chunks to `XCpCtx`, recovers from failing replicas, and steals work from slower or failed peers.

## Important APIs, Types, And Functions
- Local `ChunkHandler` is a `ResponseHandler` for async reads. It converts `AnyObject` responses into `PageInfo`, validates returned length, deletes buffers on errors, reports to the owning source, and self-deletes.
- `XCpSrc::Start`, static `Run`, and `StartDownloading` implement thread startup and the main worker loop.
- `Initialize` opens the next available URL, applies `ReadRecovery`, checks security/local metalink conditions for page-read support, stats unknown file size, publishes it to the context, and obtains the first block.
- `Recover` opens another URL, moves all ongoing chunks to `pRecovered`, clears outstanding work, and resets transfer-rate accounting.
- `ReadChunks` prioritizes recovered chunks, then reads new chunks from the current block up to `pParallel` asynchronous operations.
- `ReportResponse` reconciles async completion, failed handles, ignored stale responses, source file closure, report queueing, byte counters, and context chunk delivery.
- `Steal` transfers work from a failed or slower source using lock ordering based on mutex addresses.
- `GetWork` obtains another block or steals from `XCpCtx::WeakestLink`.
- `TransferRate` computes bytes per second using accumulated transfer time plus current active duration.

## Control Flow
The worker starts by calling `Initialize`. If initialization fails, it stops, wakes file-size waiters, and pushes a null chunk to prevent the consumer from blocking. The main loop calls `ReadChunks`. `suPartial` means no new local work remains but async reads are outstanding, so the source may request another block. `suDone` means no outstanding or local work; the source tries to get more work, then idles via `XCpCtx::AllDone`, periodically waking to steal degraded work. When an async status arrives from `pReports`, errors trigger `Recover`; if no replica remains, the source stops, wakes idle peers, pushes a null chunk, and waits until its outstanding work has been stolen or the copy completes.

## State And Persistence Behavior
`XCpSrc` owns an active `File*`, failed file handles tracked with outstanding counts, current URL, current block cursor/end, ongoing and recovered chunk maps keyed by offset, async status queue, transfer counters, and an atomic running flag. It holds a reference to `XCpCtx` for its lifetime. Buffers allocated for reads are transferred into `PageInfo` on success and eventually freed by the copy consumer or cleanup helpers. No durable state is written.

## Dependencies And Integration Points
The file integrates `XrdCl::File`, `ResponseHandler`, `AnyObject`, `PageInfo`, `XCpCtx`, `DefaultEnv`, `Utils::HasPgRW`, XRootD copy constants, pthreads, atomics, and logging. It is tightly coupled to `XCpCtx` block allocation and sink semantics and to the File async API's callback ownership model.

## Risks And Edge Cases
- In `Recover`, the page-read support condition differs from `Initialize` (`pFile->IsSecure()` check appears inverted), which may be intentional or a subtle inconsistency.
- `StartDownloading` contains a busy wait `while( HasData() && !pCtx->AllDone() );` after unrecoverable failure.
- `ReportResponse` must handle stale async responses after recovery or stealing; mistakes can double-free buffers or leak file handles.
- Work stealing removes ongoing chunks from another source; late responses from that source must be ignored by the erased-offset path.
- `TransferRate` adds one second to avoid division by zero, but sources with no data can still appear very slow and be selected as weak links only when `HasData()` is true.
- The code relies on manual self-deleting handlers and manual reference counts.

## Test Signals
Tests should cover failed open/stat and recovery to later replicas, length mismatch in `ChunkHandler`, stale async responses after recovery, PgRead enablement based on environment and protocol, chunk stealing from failed, recovered, block, and ongoing maps, and consumer wakeup on null chunk after source failure.
