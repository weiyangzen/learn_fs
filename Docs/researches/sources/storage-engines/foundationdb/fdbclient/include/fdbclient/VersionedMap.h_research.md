<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h

## Purpose
`VersionedMap.h` implements a partially persistent ordered map backed by a randomized treap-like persistent tree. It supports reading historical versions, creating new versions, mutating the latest version, and forgetting old roots.

## Important APIs, Types, and Functions
Important pieces include `DeferredCleanupWorklist`, `deferredCleanupActor`, namespace `PTreeImpl` with `PTree`, `PTreeFinger`, `insert`, `remove`, `removeFinger`, `split`, `append`, `compact`, `validate`, and traversal helpers, `ValueOrClearToRef`, and template `VersionedMap<K,T>` with version/root management, insert/erase, compaction, iterators, `ViewAtVersion`, historical lookup helpers, and `isClearContaining`.

## Control Flow
Each version points to a root in an ordered deque. `createNewVersion` appends a new root snapshot. Mutations update the latest root using persistent tree nodes that can hold an auxiliary pointer to avoid full path copying. Historical reads choose the newest root not greater than the requested version and traverse with version-aware child selection. Forgetting old versions erases old roots and can asynchronously drain uniquely owned tree nodes in bounded batches.

## State and Persistence Behavior
`VersionedMap` is in-memory MVCC state. Storage servers and read-your-writes logic use it to retain historical key-value views, clear ranges, and mutation snapshots. It does not directly persist to disk, but it models durable versioned database contents and contributes to memory accounting through `overheadPerItem`.

## Dependencies and Integration Points
It depends on Flow references, fast allocation, indexed-set-style map pairs, FDB types, randomness, and actor yielding. It integrates with storage-server MVCC maps, `WriteMap`, mutation logs, and `StorageServerInterface::mvccStorageBytes`.

## Risks and Edge Cases
Persistent tree correctness is subtle: version numbers must increase monotonically, fingers are invalidated by mutation, and auxiliary pointer compaction must not remove data still reachable by retained versions. Random priority balance is probabilistic. Recursive reference destruction is avoided by deferred cleanup, but cancellation and ownership checks are important. `getNextOldestVersion` assumes at least two roots.

## Test Signals
Signals include versioned map unit tests, historical read tests, random insert/erase validation, compaction and forget-version tests, storage-server MVCC simulation tests, memory accounting checks, and stress tests with long retained-version windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h -->
