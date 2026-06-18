# sources/object-store/minio/cmd/namespace-lock.go

This file defines MinIO namespace locking for object operations. It abstracts local and distributed read/write locks behind `RWLocker`, tracks lock contexts, manages local lock maps with reference counts, and delegates distributed locks to `dsync.DRWMutex`.

Core APIs include `newNSLock`, `nsLockMap.NewNSLock`, local `lock`/`unlock`, `localLockInstance.GetLock/GetRLock/Unlock/RUnlock`, `distLockInstance.GetLock/GetRLock/Unlock/RUnlock`, and `getSource`. Local mode stores `resource -> *nsLock` in `nsLockMap.lockMap`; each acquire increments `ref`, blocks on `lsync.LRWMutex`, and removes the map entry after failed acquisition or final unlock. Multi-path locks sort paths before construction to reduce deadlock risk and unwind previously acquired locks if a later path times out. Distributed mode creates a `dsync.DRWMutex` over prefixed paths and passes timeout and retry settings from `dynamicTimeout`.

State is in memory: the global local lock server, local lock maps, operation IDs, and contexts with cancel functions. There is no persistence. Integration points are all object-layer critical sections, distributed erasure lock servers, logger critical paths, timeout telemetry, and `runtime.Caller` source attribution.

Risks: local ref counting is concurrency-sensitive; a skipped race test documents historical risk around map entry deletion and competing lockers. Distributed read locking calls `GetRLock(ctx, cancel, ...)` while write locking uses `newCtx`, so cancellation behavior should be reviewed carefully. `getSource` tests hard-code line numbers and are fragile.
