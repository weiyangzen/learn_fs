## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance.go

Purpose: manages an MRD pool for one file inode, including lazy pool creation, generation-aware pool replacement, reads, refcounting, inactive LRU caching, eviction, and destruction.

Important APIs/types/functions: `MrdInstance`, `NewMrdInstance`, `SetMinObject`, `GetMinObject`, `getMRDEntry`, `Read`, `ensureMRDPool`, `RecreateMRD`, `closePool`, `closePoolWithTimeout`, `Destroy`, `getKey`, `IncrementRefCount`, `DecrementRefCount`, `handleEviction`, `Size`, and `RefCount`.

Control flow: reads lazily ensure a pool, get the next valid entry, recreate invalid entries, issue `mrd.Add` into a bytes buffer backed by the caller buffer, and wait for callback or context cancellation depending on `IgnoreInterrupts`. Object generation changes in `SetMinObject` swap in a new pool; same generation only updates metadata. Refcount zero inserts the instance into an LRU cache, and evicted inactive instances close pools outside locks.

State/persistence behavior: in-memory state includes object metadata, bucket, MRD pool pointer, refcount, inode ID, cache, and config. It does not persist data locally, but maintains remote read handles within MRD pools. Pool closing is asynchronous with a 120-second warning timeout.

Dependencies/integration: integrates `MRDPool`, LRU cache, config, logger, monitor metrics, GCS bucket/MRD APIs, and FUSE inode IDs. `KernelMRDReader` uses it for rapid bucket reads.

Risks/test signals: lock ordering is important across refcount, cache, and pool locks. `Destroy` warns if active users remain. Asynchronous close may delay resource release. Tests cover creation, reads, invalid entry recreation, cancellation, refcount/LRU races, generation swap, timeout logging, and error paths.
