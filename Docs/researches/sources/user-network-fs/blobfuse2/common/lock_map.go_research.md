# sources/user-network-fs/blobfuse2/common/lock_map.go
## sources/user-network-fs/blobfuse2/common/lock_map.go

Purpose: provides a keyed lock registry for file-level exclusive locking, handle counts, and download timestamps.

Important APIs/types/functions: `LockMapItem`, `LockMap`, `NewLockMap`, `Get`, `Delete`, `Locked`, and item methods `Lock`, `Unlock`, `Inc`, `Dec`, `Count`, `SetDownloadTime`, `DownloadTime`.

Control flow: `LockMap.Get` uses `sync.Map.LoadOrStore` to return an existing or new `LockMapItem` for a name. `Lock` acquires the item mutex and marks `exLocked`; `Unlock` clears the flag then releases the mutex. `Inc`/`Dec` adjust `handleCount`, and timestamp methods write/read `downloadTime`.

State and persistence: all state is in memory. `sync.Map` protects map operations, and the item mutex protects the lock critical section, but `handleCount`, `exLocked`, and `downloadTime` are read/written without consistent locking outside `Lock`/`Unlock`.

Dependencies/integration: standard `sync` and `time`; likely used by filesystem/cache components to coordinate per-path operations.

Risks: `Locked`, `Inc`, `Dec`, `Count`, and timestamp methods are not concurrency-safe relative to each other. `Dec` can underflow the uint32 count. `Delete` can remove an item while callers still hold references. No tests are present in this subset.

Test signals: absent direct tests; concurrency semantics need review in callers.
