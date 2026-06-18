# sources/storage-engines/foundationdb/fdbclient/ReadYourWrites.actor.cpp

## Purpose
`ReadYourWrites.actor.cpp` implements `ReadYourWritesTransaction`, the client-side transaction wrapper that provides FoundationDB read-your-writes semantics. It merges local mutations with cached snapshot reads, tracks conflict ranges, integrates special keyspace behavior, manages watches, options, retries, timeouts, and materializes buffered writes into the underlying native transaction at commit.

## Important APIs, Types, and Functions
- `RYWImpl` is an internal helper class containing request structs (`GetValueReq`, `GetKeyReq`, `GetRangeReq`, `GetMappedRangeReq`) and most read/commit actors.
- `read` overloads implement get, getKey, forward/reverse getRange, and limited getMappedRange behavior over either `SnapshotCache::iterator` or `RYWIterator`.
- `readThrough` bypasses the RYW overlay when `READ_YOUR_WRITES_DISABLE` is set and clips inaccessible system keys.
- `addConflictRange` and `updateConflictMap` derive read conflict ranges from resolved reads and local write-map state.
- `resolveKeySelectorFromCache`, `getKnownKeyRange`, `skipUncached`, `countUncached`, and their reverse variants drive incremental range reads and cache population.
- `triggerWatches`, `watch`, `commit`, `onError`, and `getReadVersion` implement transaction lifecycle behavior.
- Public `ReadYourWritesTransaction` methods wrap get/getRange/getMappedRange, conflict range APIs, mutations, atomic ops, commit, reset, cancel, options, debug logging, and special conflict-range introspection.

## Control Flow and State
Reads choose one of three paths: direct native transaction reads if RYW is disabled, snapshot-cache reads if snapshot RYW is disabled, or full RYW overlay reads through `RYWIterator`. Unknown cache ranges trigger native snapshot reads, insert known ranges into `SnapshotCache`, then re-resolve selectors. Serializable reads add conflicts only for unmodified or dependent-write segments where server-side state can affect the result.

Writes are buffered in `WriteMap` unless RYW is disabled. `set`, `clear`, and `atomicOp` validate key/value limits, update approximate transaction size, add conflict metadata unless disabled for the next write, and trigger local watches. At commit, the wrapper waits for outstanding reads, optionally commits special keyspace configuration changes, writes buffered clears before sets/atomic ops into the native transaction, forwards read conflicts, and commits the native transaction.

`onError` delegates retry policy to the native transaction, enforces retry limits, logs debug information, and resets the RYW cache/write/conflict/watch state for retry.

## State and Persistence Behavior
The durable commit is performed only by the underlying `Transaction`. Before commit, all RYW state is in memory: `arena`, `SnapshotCache`, `WriteMap`, `readConflicts`, `watchMap`, `nativeReadRanges`, `nativeWriteRanges`, versionstamp key tracking, special keyspace write map, timeout actor, retry counters, and persistent option vectors. `resetRyow` cancels old in-flight work through `resetPromise` and rebuilds all transient state.

## Dependencies and Integration Points
The file integrates `ReadYourWrites.h`, `NativeAPI.actor.h`, atomic mutation helpers, `DatabaseContext`, `SpecialKeySpace`, `StatusClient`, leader monitoring, Flow coroutine utilities, and actor compiler support. It is central to the FDB C/API transaction behavior and must preserve compatibility across API versions, especially for special keys, versionstamps, and option semantics.

## Risks and Edge Cases
- Range selector resolution is complex in both directions and must handle unknown ranges, single-key clears, row/byte limits, `readToBegin`, `readThroughEnd`, and inaccessible system-key boundaries.
- `getMappedRange` intentionally does not fully implement RYW; it performs native reads and throws `get_mapped_range_reads_your_writes` if relevant ranges were locally modified.
- Versionstamped key/value operations create unreadable ranges and special write-conflict behavior until the versionstamp is known.
- Using a transaction during commit sets `resetPromise` unless protection is disabled.
- API-version conditionals change reset-after-commit behavior, special key handling, mutation suffix compatibility, and cancellation semantics.
- Watch handling has to reconcile local writes racing with initial read and native watch registration.

## Test Signals
Direct tests live heavily in related iterator/write-map files, while this file exposes many simulation-code probes. High-value tests include forward/reverse range parity, conflict range special-key introspection, retries after `onError`, timeout behavior, special keyspace reads/writes by API version, versionstamp conflict keys before/after commit, watch triggering by local writes, disabled RYW direct-through behavior, and getMappedRange modified-range rejection.
