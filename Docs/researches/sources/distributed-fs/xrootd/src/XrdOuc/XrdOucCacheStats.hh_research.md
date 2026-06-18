# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheStats.hh

## Purpose
Provides a thread-serialized statistics container for cache usage. It groups cumulative cache I/O counters, file counters, disk and memory state, and POSIX-layer deferred-open/close counters.

## Important APIs, Types, And Functions
`XrdOucCacheStats::CacheStats` is a POD record stored as public member `X`. Counters include read/write bytes (`BytesRead`, `BytesGet`, `BytesPass`, `BytesWrite`, `BytesPut`), hit/miss/pass and preread counts, file lifecycle counts, disk and memory gauges, and deferred-file counters. Methods `Get`, `Add`, and `Set` copy, aggregate, or replace selected portions under `XrdSysMutex`. Scalar helpers `Add(long long&, long long)`, `Count`, and `Set(long long&, long long)` update individual counters.

## Control Flow
Callers update `X` either directly while holding `Lock()`/`UnLock()` or through scalar helpers. `Get` snapshots the full POD with `memcpy`; `Add` aggregates only activity counters; `Set` refreshes gauge-like file/disk/memory fields. Construction zeroes the POD.

## State And Persistence
All state is in-memory. The mutex guards concurrent updates but the public `X` member allows callers to bypass locking unless they follow the convention. No counters are persisted by this class.

## Dependencies And Integration Points
Depends on `XrdSysAtomics.hh` and `XrdSysPthread.hh`. It is meant to be embedded in cache objects and integrated with monitoring/statistics export paths that snapshot or merge cache counters.

## Risks And Test Signals
Risks include public mutable state, inconsistent use of lock helpers, and `Add(XrdOucCacheStats&)` intentionally omitting some counters such as deferred opens/closes and gauges. Test signals should cover concurrent counter increments, aggregate semantics, snapshot consistency, and monitoring output after cache reads, writes, purges, and open/close events.
