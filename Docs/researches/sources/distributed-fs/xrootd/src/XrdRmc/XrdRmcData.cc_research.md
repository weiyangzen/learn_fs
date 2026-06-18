# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.cc

## Purpose

`XrdRmcData.cc` implements the `XrdOucCacheIO` wrapper used for each attached I/O object in the RMC cache. It performs cached reads, write-through updates, truncation, detach cleanup, per-file statistics, and manual/automatic preread scheduling.

## Important APIs, Types, And Functions

- Constructor maps attach options (`optFIS`, `optRW`) into local flags, copies cache geometry, initializes preread queues, configures automatic preread parameters, and sets read/preread/write locks based on cache thread-safety options.
- `Detach()` waits for prereads to stop, serializes detach, asks `XrdRmcReal` to detach the underlying object, merges stats, optionally logs them, and deletes itself.
- `Read(Buff, Offs, rLen)` handles both preread requests (`Buff == nullptr`) and normal cached reads, including bypass for reads larger than `maxCache`.
- Private `Read(Now, Buff, Offs, rLen)` implements the large-read bypass path, mixing cache hits with direct I/O for misses.
- `Write()` writes through to the underlying object first, then updates cached pages that are already present.
- `Trunc()` invalidates cached pages from the truncation point and delegates the real truncate.
- `Preread()`, `Preread(Offs, rLen, Opts)`, `Preread(aprParms&)`, `QueuePR()`, and `setAPR()` implement asynchronous and automatic preread behavior.

## Control Flow

Normal reads validate bounds, optionally remember recent reads for automatic preread suppression, then fetch page buffers through `Cache->Get()`. Hits copy from cached pages; misses cause `XrdRmcReal` to read a segment from the underlying object. Each page is released through `Cache->Ref()`, with structured-file accounting when enabled. After a successful read, automatic preread can enqueue the next segment range.

Large reads over `maxCache` avoid filling the cache. That path cancels overlapping prereads, copies any existing cache hits, accumulates contiguous cache misses into direct `ioObj->Read()` calls, and records pass-through statistics. Writes are strictly write-through: failure to write the underlying object aborts cache updates.

Preread requests are stored in an eight-entry ring. The preread worker calls `Preread()`, consumes queued ranges, faults pages into the cache with `isNew` and optionally `isSUSE`, and updates preread stats. Detach coordinates with active prereads through `prStop` and semaphores.

## State And Persistence

All state is per attached file wrapper: statistics, read/write lock, underlying `ioObj`, virtual file number `VNum`, cache geometry, flags, recent-read ring, preread queue, automatic preread tuning, and active/stop markers. Cache contents live in `XrdRmcReal` memory, not this object. No state is persisted to disk.

## Dependencies And Integration Points

The class depends on `XrdRmcReal`, `XrdOucCacheIO`, `XrdOucCacheStats`, `XrdSysXSLock`, `XrdSysMutex`, and `XrdSysSemaphore`. It is created by `XrdRmcReal::Attach()` and deleted after successful detach.

## Risks And Edge Cases

- `Preread(long long Offs, int rLen, int Opts)` has a condition that returns when the request appears valid, meaning only invalid-looking requests fall through to `QueuePR()`; this is suspicious and should be tested.
- Detach comments acknowledge that failed detach can leak the wrapper because it will not retry.
- Cache locking depends on caller-supplied `Serialized` and `ioMTSafe` options; incorrect flags can cause over-serialization or races.
- Large-read path mixes direct I/O and cache hits; partial direct reads return the accumulated destination length, so EOF and short reads require careful validation.
- Fixed preread queue depth discards or skips older entries under pressure.

## Test Signals

Tests should cover small cached reads, repeated hits, reads larger than `maxCache`, read overflow and negative offsets, `Buff == nullptr` preread requests, automatic preread enable/disable based on performance, write-through update of existing cached pages, read-only write rejection, truncation invalidation, detach with active prereads, and structured-file single-use behavior.
