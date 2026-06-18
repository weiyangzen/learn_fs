## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.cc

Purpose: implements reusable async response handlers that translate XrdCl responses into `XrdOucCacheIOCB` completions.

Important APIs/functions: static `Alloc`, `HandleResponse`, `Recycle`, `Sched`, and helper thread entry `callDoIt`.

Control flow: `Alloc()` pulls a handler from a bounded free list or allocates one, initializes callback/file/offset/result/type/checksum fields, and returns it to the I/O issuer. `HandleResponse()` maps failed status to negative errno, extracts read length from `ChunkInfo`, extracts page length/checksums/repair count from `PageInfo`, optionally computes checksums when forced, updates file size for writes, deletes response objects, unreferences the file, and schedules `DoIt()` through the global scheduler or a new thread. `Sched()` handles immediate errors similarly.

State and persistence: static free list protected by `myMutex`, configurable `maxFree`; per-handler transient callback, file, checksum, offset, result, and type. No durable state.

Dependencies/integration: uses `XrdScheduler`, `XrdOucCacheIOCB`, `XrdOucPgrwUtils`, `XrdPosixFile`, and `XrdPosixMap`. It is central to all async file/cache I/O completion.

Risks: for `isWrite`, size update uses `offset+result`; if `result` is an initial requested length rather than actual completion length, partial-write semantics need scrutiny. Scheduling fallback creates a thread per completion when no scheduler exists. Free-list reuse demands all fields be reset in `Alloc()`.

Test signals: async read/readv/write/sync/page-read success and error; forced checksum generation; repair count propagation; no-scheduler fallback; free-list max behavior.
